"""Tests: Vercel entrypoint serves the real app with original paths.

Vercel's Python runtime loads the app from the entrypoint declared in
pyproject.toml ([tool.vercel] entrypoint) and routes every request to
it, so the app sees the original request path — no vercel.json rewrite
is involved. A rewrite to /api/index used to mask every path as
PATH_INFO=/api/index and made the live NoteVault Bharat app 404 on /
and every other path; that failure mode is pinned in
tests/test_vercel_routing_regression.py, and the diagnosis is in
deployment/DEPLOYMENT_RUNBOOK.md.
"""
import importlib
import json
import threading
import tomllib
import urllib.request
from pathlib import Path
from wsgiref.simple_server import make_server as make_wsgi_server

import pytest

_REPO = Path(__file__).resolve().parent.parent
_ENTRYPOINT = "wsgi:application"

_STUDENT_TEXT = (
    "I am a 19 year old student from Meerut, Uttar Pradesh. "
    "My family income is 2 lakh per year. I want a scholarship for college."
)
_STUDENT_FORM = {
    "age": "19", "annual_income": "300000", "gender": "female",
    "occupation": "student", "sc_st": True, "post_matric": True,
}


def _declared_entrypoint():
    with (_REPO / "pyproject.toml").open("rb") as fh:
        cfg = tomllib.load(fh)
    return cfg["tool"]["vercel"]["entrypoint"]


def _load_entrypoint():
    module_name, attr = _declared_entrypoint().split(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, attr)


@pytest.fixture(scope="module")
def live():
    server = make_wsgi_server("127.0.0.1", 0, _load_entrypoint())
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


def _get(base, path):
    with urllib.request.urlopen(base + path) as resp:
        return resp.status, resp.read()


def _post(base, path, obj):
    req = urllib.request.Request(
        base + path, data=json.dumps(obj).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read()


def test_vercel_entrypoint_declared_in_pyproject():
    assert _declared_entrypoint() == _ENTRYPOINT


def test_vercel_entrypoint_resolves_to_callable_wsgi_app():
    assert callable(_load_entrypoint())


def test_vercel_json_has_no_rewrites():
    cfg = json.loads((_REPO / "vercel.json").read_text(encoding="utf-8"))
    assert "rewrites" not in cfg


def test_vercel_api_shim_is_gone():
    # No api/index.py shim may exist: the app has exactly one
    # entrypoint, and a stale /api/index function would double-route.
    assert not (_REPO / "api" / "index.py").exists()


def test_vercel_homepage_serves_ui(live):
    status, body = _get(live, "/")
    assert status == 200
    assert b"SchemeSathi" in body


def test_vercel_health_eighteen_schemes(live):
    status, body = _get(live, "/health")
    assert status == 200
    data = json.loads(body)
    assert data["status"] == "ok"
    assert data["app"] == "schemesathi"
    assert data["schemes"] == 18


def test_vercel_schemes_list(live):
    status, body = _get(live, "/api/schemes")
    assert status == 200
    data = json.loads(body)
    assert len(data["schemes"]) == 18
    for s in data["schemes"]:
        assert s["id"] and s["name"] and s["docs"] and s["steps"]


def test_vercel_match_hinglish_student_sentence(live):
    status, body = _post(live, "/api/match", {"text": _STUDENT_TEXT})
    assert status == 200
    data = json.loads(body)
    assert data["profile"]["age"] == 19
    assert data["profile"]["annual_income"] == 200000
    assert data["profile"]["state"] == "Uttar Pradesh"
    assert len(data["results"]) == 18
    assert data["summary"] == {
        "ELIGIBLE": 2, "CLOSE": 0, "NEEDS INFO": 0, "NOT ELIGIBLE": 16,
    }
    verdicts = {r["id"]: r["verdict"] for r in data["results"]}
    assert verdicts["pmjdy"] == "ELIGIBLE"
    assert verdicts["pmkvy"] == "ELIGIBLE"


def test_vercel_whatif_income_drop_opens_scheme(live):
    status, body = _post(live, "/api/match", {"profile": _STUDENT_FORM})
    assert status == 200
    verdicts = {r["id"]: r["verdict"] for r in json.loads(body)["results"]}
    assert verdicts["post-matric-sc"] == "CLOSE"
    status, body = _post(live, "/api/whatif", {
        "profile": _STUDENT_FORM,
        "overrides": {"annual_income": 200000},
    })
    assert status == 200
    verdicts = {r["id"]: r["verdict"] for r in json.loads(body)["results"]}
    assert verdicts["post-matric-sc"] == "ELIGIBLE"
