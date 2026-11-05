"""SchemeSathi web server — Python 3 stdlib only, no dependencies.

Serves the single-page UI and a small JSON API. Everything runs locally;
no request ever leaves the machine, no data is stored on disk.

Endpoints:
  GET  /            the app (app/index.html)
  GET  /health      {"status": "ok", "schemes": N, ...}
  GET  /api/schemes list of schemes (rules, benefits, docs, steps)
  POST /api/match   {text} or {profile} -> parsed profile + all verdicts
  POST /api/whatif  {profile, overrides} -> re-matched results

Run:  python3 run.py            (serves on http://127.0.0.1:8765)
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from schemes import (  # noqa: E402
    SCHEMES, CATEGORIES, OFFICIAL_PORTAL, DATA_AS_OF, SCHEME_COUNT,
    parse_profile, profile_from_form, match_all, what_if, summarise,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
# Render (and most PaaS hosts) set PORT and require binding 0.0.0.0.
# Locally, default to 127.0.0.1:8765 so nothing is exposed on the LAN.
PORT = int(os.environ.get("PORT") or os.environ.get("SCHEMESATHI_PORT", "8765"))
HOST = "0.0.0.0" if "PORT" in os.environ else "127.0.0.1"


def _public_scheme(s):
    return {
        "id": s["id"], "name": s["name"], "name_hi": s["name_hi"],
        "ministry": s["ministry"], "category": s["category"],
        "benefit": s["benefit"], "blurb": s["blurb"],
        "docs": s["docs"], "steps": s["steps"],
    }


def _public_result(r):
    s = r["scheme"]
    return {
        "id": s["id"], "name": s["name"], "name_hi": s["name_hi"],
        "ministry": s["ministry"], "category": s["category"],
        "benefit": s["benefit"], "blurb": s["blurb"],
        "docs": s["docs"], "steps": s["steps"],
        "verdict": r["verdict"], "checks": r["checks"],
        "missing": r["missing"],
    }


def _serialisable_profile(p):
    return {
        "age": p.get("age"), "annual_income": p.get("annual_income"),
        "gender": p.get("gender"),
        "occupations": sorted(p.get("occupations") or []),
        "state": p.get("state"),
        "flags": sorted(p.get("flags") or []),
    }


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # keep stdout clean
        sys.stderr.write("[schemesathi] " + fmt % args + "\n")

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, content_type):
        with open(path, "rb") as fh:
            body = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except (ValueError, UnicodeDecodeError):
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send_file(INDEX_PATH, "text/html; charset=utf-8")
        elif parsed.path == "/health":
            self._send_json({
                "status": "ok", "app": "schemesathi", "schemes": SCHEME_COUNT,
                "categories": CATEGORIES, "data_as_of": DATA_AS_OF,
                "official_portal": OFFICIAL_PORTAL,
                "privacy": "on-device only — nothing leaves this machine",
            })
        elif parsed.path == "/api/schemes":
            self._send_json({
                "schemes": [_public_scheme(s) for s in SCHEMES],
                "categories": CATEGORIES,
                "data_as_of": DATA_AS_OF,
                "official_portal": OFFICIAL_PORTAL,
            })
        else:
            self._send_json({"error": "not found"}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/match":
            data = self._read_json()
            if "profile" in data and isinstance(data["profile"], dict):
                profile = profile_from_form(data["profile"])
            else:
                profile = parse_profile(data.get("text", ""))
            results = match_all(profile)
            self._send_json({
                "profile": _serialisable_profile(profile),
                "summary": summarise(results),
                "results": [_public_result(r) for r in results],
                "official_portal": OFFICIAL_PORTAL,
                "data_as_of": DATA_AS_OF,
            })
        elif parsed.path == "/api/whatif":
            data = self._read_json()
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
            self._send_json({
                "summary": summarise(results),
                "results": [_public_result(r) for r in results],
            })
        else:
            self._send_json({"error": "not found"}, status=404)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("SchemeSathi running at http://%s:%d  (Ctrl+C to stop)" % (HOST, PORT))
    print("Schemes loaded: %d | data snapshot: %s | fully on-device" % (SCHEME_COUNT, DATA_AS_OF))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
