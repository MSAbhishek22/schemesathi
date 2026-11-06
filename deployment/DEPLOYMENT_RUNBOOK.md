# DEPLOYMENT RUNBOOK — SchemeSathi (SLAY HACKS 2026)

> Status: READY FOR DEPLOY. Vercel entrypoint built, tested 38/38,
> manifest regenerated — NOT yet pushed, NOT yet deployed, NOT live.
> The push and the Vercel import are the parent's steps.

## Target
- Provider: **Vercel Hobby** (free tier, GitHub OAuth signup — no
  password, no card). A Vercel account already exists (GitHub OAuth,
  email msabhishekanni10@gmail.com) and NoteVault Bharat is LIVE on
  it at https://notevault-bharat.vercel.app.
- Why NOT Render: the original plan was Render free tier, but Render
  now demands a card even for free-tier deploys on new accounts
  (proven 2026-11-06 on NoteVault Bharat — "Add Card" modal on
  deploy). **STOP at once if any step asks for a card or payment.**
- Runtime: Python 3.12, stdlib only — no dependencies to install.
- Expected URL: `https://schemesathi.vercel.app` (or the generated
  name Vercel assigns at import).

## What was built for Vercel (local only — NOT pushed, NOT deployed)
- `wsgi.py` — WSGI adapter exposing `application`. Same routes and
  JSON shapes as `app/server.py` (GET /, /index.html, /health,
  /api/schemes; POST /api/match, /api/whatif; 404
  `{"error": "not found"}`), calling the same `schemes.py` functions
  and the same shape helpers from `server.py`. `run.py` and
  `app/server.py` are untouched.
- `pyproject.toml` — `[tool.vercel] entrypoint = "wsgi:application"`.
  The Python runtime loads the WSGI app from that module and routes
  EVERY request to it with the original path.
- `vercel.json` — `{}`. **No rewrite.** A rewrite to `/api/index`
  used to mask every path as PATH_INFO=/api/index and made the live
  NoteVault Bharat app 404 on / and every other path (first deploy,
  6 Nov 18:46 IST). Vercel provides no header carrying the original
  path to a rewritten function, so the fix is to not rewrite at all.
  That failure mode is pinned in
  `tests/test_vercel_routing_regression.py`.
- `tests/test_vercel_entrypoint.py` — 9 tests: entrypoint declared
  and resolvable, no rewrites in vercel.json, no `api/index.py` shim,
  homepage, /health (18 schemes), /api/schemes (18), Hinglish
  student match (age 19, income 200000, ELIGIBLE 2: pmjdy, pmkvy),
  what-if income drop (post-matric-sc CLOSE → ELIGIBLE).
- `tests/test_vercel_routing_regression.py` — 4 tests: the old
  rewrite reproduced locally (PATH_INFO forced to /api/index → 404
  on / and /health), the entrypoint serving original paths, match +
  what-if, and a direct GET /api/index answering the app's own 404
  without breaking later routing.

## Validation (Linux sandbox, Python 3.12.3, 6 Nov 2026)
- Full suite: **38/38 pytest PASS** (25 existing + 13 new Vercel
  tests).
- WSGI smoke test via wsgiref + curl: GET / 200 (34,238 bytes),
  GET /health 200 (18 schemes), GET /api/schemes 200 (18),
  POST /api/match correct profile + summary, GET /nope 404.

## Honest behaviour differences vs the local server
- **Stateless, so none.** The app keeps no per-instance state (no
  budget counter, no writes); every request is computed fresh from
  the bundled scheme data. Cold starts add ~1 s on first request
  after idle; no Render-style sleep takes the site offline.
- **Read-only filesystem is fine.** The app never writes; index.html
  and scheme data are read via `__file__`-based absolute paths.
- **Hobby limits** (ample for a demo): 1M function invocations/mo,
  100 GB transfer/mo. Hobby is non-commercial personal use — fits a
  hackathon demo.
- **Possible signup friction (unverified for India):** Vercel
  community reports some GitHub signups are asked for SMS/phone
  verification. Not a card gate; if it appears, stop and report.

## Steps (parent's steps — push, then browser deploy)
1. Push this folder to `MSAbhishek22/schemesathi` (main) with the
   user-approval card. Manifest (regenerated after tests, NUL-
   delimited, 19 files):
   `~/workspace/hackathons/slay-hacks-paths`. Last pushed head was
   `86e1de7`; verify the new head with `list_commits` after the
   push. Snapshot pushes do NOT delete files — nothing needs
   deleting here (no `api/index.py` shim was ever created).
2. Dispatch a browser task: Vercel (already signed in via GitHub
   OAuth) → Add New Project → import repo
   `MSAbhishek22/schemesathi`, Hobby plan, project name
   `schemesathi`, Python preset, no build command, no env vars →
   Deploy. **Stop at once if a card is asked; stop and report if
   phone/SMS verification appears.** The import form needs the
   entrypoint only via `pyproject.toml` — nothing to type: Vercel
   reads `[tool.vercel] entrypoint = "wsgi:application"` from the
   repo. Expected URL: `https://schemesathi.vercel.app`.
3. Verify the live URL (GET / 200 + "SchemeSathi", GET /health 200
   with 18 schemes, POST /api/match student example, POST
   /api/whatif) and record URL + commit SHA in
   `deployment/RELEASE_MANIFEST.json` (status becomes DEPLOYED,
   NOT SUBMITTED until the Devpost filing).
4. Record the demo video from the live URL only (2–4 min).

## Health check
- `GET /health` returns `{"status": "ok", "schemes": 18, ...}`.
- `GET /` returns the app (34,238 bytes HTML, no external assets).

## Rollback
- Vercel keeps prior deployments; roll back to the previous
  deployment in the dashboard. The app is stateless (in-memory
  only), so rollback is safe.

## Known deploy blockers
- Render free tier is card-gated on new accounts (proven 6 Nov
  2026) — do not retry Render. Vercel is the route; Replit is the
  second fallback (30-day link expiry, 15-min idle sleep).
