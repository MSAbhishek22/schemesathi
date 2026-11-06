"""Regression test: the front end must read the API's flat result shape.

On 2026-11-07 the Codespace recording probe found the live site's core
flow broken: clicking "Check my schemes" threw
"Cannot read properties of undefined (reading 'id')" and no verdicts ever
rendered. Root cause: /api/match returns FLAT results (id, name,
category, verdict, checks, missing at the top level — see
app/server.py::_public_result), but app/index.html rendered them as if
each result carried a nested `scheme` object (`r.scheme.category`,
`const s = r.scheme`, `x.scheme.id`). The 38-test suite never caught it
because no test exercised the renderer against a real API payload.

These tests pin the contract on both sides: the API stays flat, the page
reads flat fields, and the page's own render functions (extracted from
the served index.html) produce real HTML for real API results.
"""
import json
import re
import subprocess
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path
from wsgiref.simple_server import make_server as make_wsgi_server

import pytest

_REPO = Path(__file__).resolve().parent.parent

_DEMO_TEXT = "I am a 19 year old student from UP, family income 2 lakh per year"
_FORM_PROFILE = {
    "age": "19", "annual_income": "300000", "gender": "female",
    "occupation": "student", "sc_st": True, "post_matric": True,
}
_FLAT_KEYS = {
    "id", "name", "name_hi", "ministry", "category", "benefit", "blurb",
    "docs", "steps", "verdict", "checks", "missing",
}


@pytest.fixture(scope="module")
def live():
    sys.path.insert(0, str(_REPO))
    from wsgi import application
    server = make_wsgi_server("127.0.0.1", 0, application)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


def _post(base, path, payload):
    req = urllib.request.Request(
        base + path, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read())


def _inline_script():
    html = (_REPO / "app" / "index.html").read_text(encoding="utf-8")
    match = re.search(r"<script>([\s\S]*?)</script>", html)
    assert match, "index.html has no inline <script> block"
    return match.group(1)


def test_api_match_returns_flat_results(live):
    status, data = _post(live, "/api/match", {"text": _DEMO_TEXT})
    assert status == 200
    assert data["summary"] == {
        "ELIGIBLE": 2, "CLOSE": 0, "NEEDS INFO": 0, "NOT ELIGIBLE": 16,
    }
    assert len(data["results"]) == 18
    for r in data["results"]:
        assert "scheme" not in r, "result must not carry a nested scheme object"
        assert _FLAT_KEYS <= set(r), f"flat result missing keys: {_FLAT_KEYS - set(r)}"


def test_frontend_reads_flat_result_fields():
    script = _inline_script()
    assert "r.scheme" not in script, "renderer still reads r.scheme"
    assert "x.scheme" not in script, "renderer still reads x.scheme"


def test_inline_script_parses():
    script = _inline_script()
    with tempfile.NamedTemporaryFile(
            "w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(script)
        path = fh.name
    proc = subprocess.run(["node", "--check", path],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def _extract_function(script, name):
    """Slice one top-level `function name(...) {...}` out of the script."""
    starts = [m.start() for m in re.finditer(
        r"(?m)^function " + re.escape(name) + r"\(", script)]
    assert len(starts) == 1, f"expected one {name} definition, found {len(starts)}"
    start = starts[0]
    following = [m.start() for m in re.finditer(r"(?m)^function ", script)
                 if m.start() > start]
    end = min(following) if following else len(script)
    return script[start:end].rstrip()


def _render_in_node(script, result):
    """Run the page's own schemeHTML() on a real API result in Node."""
    funcs = "\n".join(_extract_function(script, n) for n in
                      ("verdictClass", "schemeHTML", "closeAdvice"))
    driver = (
        funcs + "\n"
        + "const result = " + json.dumps(result) + ";\n"
        + "const html = schemeHTML(result);\n"
        + "for (const needle of [result.name, result.verdict, "
        + "result.docs[0], result.benefit]) {\n"
        + "  if (!html.includes(needle)) {\n"
        + "    console.error('missing from rendered HTML:', needle);\n"
        + "    process.exit(1);\n"
        + "  }\n"
        + "}\n"
        + "console.log('render OK', result.id, result.verdict);\n"
    )
    with tempfile.NamedTemporaryFile(
            "w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(driver)
        path = fh.name
    proc = subprocess.run(["node", path], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    return proc.stdout.strip()


def test_page_renderer_renders_real_api_results(live):
    script = _inline_script()
    _, data = _post(live, "/api/match", {"text": _DEMO_TEXT})
    eligible = next(r for r in data["results"] if r["verdict"] == "ELIGIBLE")
    out = _render_in_node(script, eligible)
    assert "render OK" in out and eligible["id"] in out

    _, form_data = _post(live, "/api/match", {"profile": _FORM_PROFILE})
    close = [r for r in form_data["results"] if r["verdict"] == "CLOSE"]
    assert close, "expected at least one CLOSE result for the form profile"
    # A CLOSE result exercises closeAdvice() inside schemeHTML().
    out = _render_in_node(script, close[0])
    assert "render OK" in out and close[0]["id"] in out
