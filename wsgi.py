"""WSGI entry point for SchemeSathi — Vercel Hobby deploy.

Stdlib only. Vercel's Python runtime loads `application` from the
entrypoint declared in pyproject.toml ([tool.vercel] entrypoint) and
routes EVERY request to it with the original path, so the app deploys
as-is — no vercel.json rewrite.

The route table mirrors Handler in app/server.py exactly (GET /,
/index.html, /health, /api/schemes; POST /api/match, /api/whatif),
calling the same schemes.py functions and the same JSON-shape helpers
from server.py, so the live app behaves identically to the local
server. run.py and app/server.py are untouched by this module.

Render was the original deploy plan, but Render now demands a card
even for free-tier deploys on new accounts (proven 2026-11-06 on
NoteVault Bharat), so Vercel Hobby is the route — the same recipe as
NoteVault Bharat, which is live on Vercel with this entrypoint model.
See deployment/DEPLOYMENT_RUNBOOK.md.

A rewrite to /api/index must never be used: Vercel provides no header
carrying the original path to a rewritten function, so the app would
see PATH_INFO=/api/index for every request and 404 on everything
(the NoteVault Bharat first-deploy failure, 2026-11-06). That failure
mode is pinned in tests/test_vercel_routing_regression.py.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from schemes import (  # noqa: E402
    SCHEMES, CATEGORIES, OFFICIAL_PORTAL, DATA_AS_OF, SCHEME_COUNT,
    parse_profile, profile_from_form, match_all, what_if, summarise,
)
from server import (  # noqa: E402
    _public_scheme, _public_result, _serialisable_profile, INDEX_PATH,
)

_REASONS = {200: "OK", 404: "Not Found"}


def _to_json(obj) -> bytes:
    # ensure_ascii=False, like server.py — scheme names carry Devanagari.
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


def _read_json(body_bytes: bytes) -> dict:
    # Mirrors server.py's _read_json: invalid JSON or a non-dict body
    # is treated as an empty object, never a 400.
    if not body_bytes.strip():
        return {}
    try:
        data = json.loads(body_bytes.decode("utf-8"))
        return data if isinstance(data, dict) else {}
    except (ValueError, UnicodeDecodeError):
        return {}


def _dispatch(method: str, path: str, body_bytes: bytes) -> tuple[int, str, bytes]:
    """Pure route dispatch. Returns (status, content-type, body bytes)."""
    if method == "GET" and path in ("/", "/index.html"):
        with open(INDEX_PATH, "rb") as fh:
            return 200, "text/html; charset=utf-8", fh.read()
    if method == "GET" and path == "/health":
        return 200, "application/json", _to_json({
            "status": "ok", "app": "schemesathi", "schemes": SCHEME_COUNT,
            "categories": CATEGORIES, "data_as_of": DATA_AS_OF,
            "official_portal": OFFICIAL_PORTAL,
            "privacy": "on-device only — nothing leaves this machine",
        })
    if method == "GET" and path == "/api/schemes":
        return 200, "application/json", _to_json({
            "schemes": [_public_scheme(s) for s in SCHEMES],
            "categories": CATEGORIES,
            "data_as_of": DATA_AS_OF,
            "official_portal": OFFICIAL_PORTAL,
        })
    if method == "POST" and path == "/api/match":
        data = _read_json(body_bytes)
        if "profile" in data and isinstance(data["profile"], dict):
            profile = profile_from_form(data["profile"])
        else:
            profile = parse_profile(data.get("text", ""))
        results = match_all(profile)
        return 200, "application/json", _to_json({
            "profile": _serialisable_profile(profile),
            "summary": summarise(results),
            "results": [_public_result(r) for r in results],
            "official_portal": OFFICIAL_PORTAL,
            "data_as_of": DATA_AS_OF,
        })
    if method == "POST" and path == "/api/whatif":
        data = _read_json(body_bytes)
        base = data.get("profile") or {}
        profile = profile_from_form(base) if isinstance(base, dict) else parse_profile("")
        overrides = data.get("overrides") or {}
        clean = {}
        if "annual_income" in overrides:
            try:
                clean["annual_income"] = int(overrides["annual_income"])
            except (TypeError, ValueError):
                pass
        if "age" in overrides:
            try:
                clean["age"] = int(overrides["age"])
            except (TypeError, ValueError):
                pass
        results = what_if(profile, **clean)
        return 200, "application/json", _to_json({
            "summary": summarise(results),
            "results": [_public_result(r) for r in results],
        })
    return 404, "application/json", _to_json({"error": "not found"})


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    raw = environ["wsgi.input"].read(length) if length else b""
    status, ctype, body = _dispatch(method, path, raw)
    start_response(
        f"{status} {_REASONS.get(status, '')}",
        [("Content-Type", ctype), ("Content-Length", str(len(body)))],
    )
    return [body]
