"""Regression tests: the Vercel rewrite bug (Nov 2026).

The first NoteVault Bharat Vercel deploy used vercel.json
{"rewrites": [{"source": "/(.*)", "destination": "/api/index"}]}.
Vercel's proxy then delivered every request to the function with
PATH_INFO=/api/index, and the app — which routes on PATH_INFO —
answered its own 404 JSON for / and every other path, even though
the function was running. Vercel provides no header or environ value
carrying the original path to a rewritten function, so the fix is to
not rewrite at all: the app is a root entrypoint ([tool.vercel]
entrypoint) and Vercel routes every request to it with the original
path. The entrypoint mechanism itself is the "original-path
mechanism". SchemeSathi uses the same recipe, so the same failure
mode is pinned here. See deployment/DEPLOYMENT_RUNBOOK.md.
"""
import importlib
import json
import threading
import tomllib
import urllib.error
import urllib.request
from pathlib import Path
from wsgiref.simple_server import make_server as make_wsgi_server

import pytest

_REPO = Path(__file__).resolve().parent.parent

_STUDENT_FORM = {
    "age": "19", "annual_income": "300000", "gender": "female",
    "occupation": "student", "sc_st": True, "post_matric": True,
}


def _load_entrypoint():
    with (_REPO / "pyproject.toml").open("rb") as fh:
        entrypoint = tomllib.load(fh)["tool"]["vercel"]["entrypoint"]
    module_name, attr = entrypoint.split(":", 1)
    return getattr(importlib.import_module(module_name), attr)


def _rewritten_to_api_index(app):
    """WSGI middleware simulating Vercel's old rewrite: every request
    arrives with PATH_INFO=/api/index, whatever the client asked for."""
    def rewritten(environ, start_response):
        environ["PATH_INFO"] = "/api/index"
        return app(environ, start_response)
    return rewritten


def _serve(app):
    server = make_wsgi_server("127.0.0.1", 0, app)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{port}"


@pytest.fixture(scope="module")
def live():
    server, base = _serve(_load_entrypoint())
    yield base
    server.shutdown()
    server.server_close()


@pytest.fixture(scope="module")
def live_rewritten():
    # The broken deployment, reproduced locally: the entrypoint behind
    # the old /(.*) -> /api/index rewrite.
    server, base = _serve(_rewritten_to_api_index(_load_entrypoint()))
    yield base
    server.shutdown()
    server.server_close()


def _fetch(base, path, method="GET", obj=None):
    data = json.dumps(obj).encode("utf-8") if obj is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(
        base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def test_old_rewrite_masked_homepage_and_health(live_rewritten):
    # The exact live symptom, pinned: with PATH_INFO forced to
    # /api/index the app 404s on / and /health. If a rewrite ever
    # returns, this is what the live site does again.
    for path in ("/", "/health"):
        status, body = _fetch(live_rewritten, path)
        assert status == 404
        assert json.loads(body) == {"error": "not found"}


def test_entrypoint_serves_original_paths(live):
    status, body = _fetch(live, "/")
    assert status == 200
    assert b"SchemeSathi" in body
    status, body = _fetch(live, "/health")
    assert status == 200
    data = json.loads(body)
    assert data["status"] == "ok"
    assert data["schemes"] == 18


def test_entrypoint_match_and_whatif(live):
    status, body = _fetch(
        live, "/api/match", method="POST", obj={"profile": _STUDENT_FORM})
    assert status == 200
    verdicts = {r["id"]: r["verdict"] for r in json.loads(body)["results"]}
    assert verdicts["post-matric-sc"] == "CLOSE"
    status, body = _fetch(
        live, "/api/whatif", method="POST",
        obj={"profile": _STUDENT_FORM,
             "overrides": {"annual_income": 200000}})
    assert status == 200
    verdicts = {r["id"]: r["verdict"] for r in json.loads(body)["results"]}
    assert verdicts["post-matric-sc"] == "ELIGIBLE"


def test_api_index_direct_request_does_not_break_routing(live):
    # /api/index is no longer a function route — just an unknown path
    # to the single app. It must answer the app's own 404, not break,
    # and the next real request must still route normally.
    status, body = _fetch(live, "/api/index")
    assert status == 404
    assert json.loads(body) == {"error": "not found"}
    status, body = _fetch(live, "/health")
    assert status == 200
    assert json.loads(body)["schemes"] == 18
