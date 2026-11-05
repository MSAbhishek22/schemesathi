# DEPLOYMENT RUNBOOK — SchemeSathi (SLAY HACKS 2026)

> Status: NOT YET DEPLOYED. This runbook is the plan; no deployment has
> been attempted (no account creation is permitted in this prep pass).

## Target
- Provider: **Render free tier** (static-site equivalent: the app is a
  Python stdlib server, so deploy as a Render **Web Service, free plan**).
- Why Render: the project already targets Render for sibling projects
  (ClinicLink render.yaml pattern); free tier needs no card at signup.
  **STOP at once if any step asks for a card or payment.**
- Runtime: Python 3.12, stdlib only — no dependencies to install.

## Steps (user's tap — do not run without the user's go-ahead)
1. Create the GitHub repo (user's tap) and push this folder.
   Suggested repo: `github.com/MSAbhishek22/schemesathi`.
2. In Render (user's account): New → Web Service → connect the repo.
   - Build command: none (stdlib only). If Render insists on one, use
     `echo ok`.
   - Start command: `python3 run.py`. The server already handles this:
     it binds `0.0.0.0:$PORT` when Render's `PORT` variable is present
     (and `127.0.0.1:8765` locally), so no code change is needed.
   - Environment: `PORT` is set by Render automatically. No secrets exist.
3. Add a `render.yaml` (or deploy via dashboard) — free plan, `python3`.
4. After deploy: open the live `.onrender.com` URL in a fresh browser,
   run the full journey (student example → expand a card → what-if),
   check console/network errors, check a mobile viewport.
5. Record the exact deployed commit SHA in
   `deployment/RELEASE_MANIFEST.json` and freeze that commit before
   recording the demo video.

## Health check
- `GET /health` returns `{"status": "ok", "schemes": 18, ...}`.
- `GET /` returns the app (34 KB HTML, no external assets).

## Rollback
- Render keeps prior deploys; roll back to the previous deploy in the
  dashboard. The app is stateless (in-memory only), so rollback is safe.

## Known deploy blockers
- None known except the account itself (user's Render signup).
- Free-tier sleep: Render free web services sleep after inactivity and
  take ~60s to wake — note this in the submission ("first load may take
  up to a minute").
