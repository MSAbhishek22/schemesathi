# RELEASE CARD — SchemeSathi (SLAY HACKS 2026)

Built 5 Nov 2026, Linux sandbox. Overall release: **IN_PROGRESS**
(Gates A–D pass; E–F BLOCKED on the user's deploy + video taps).

| Deliverable | Evidence |
|---|---|
| Project identity | SchemeSathi — on-device, explainable navigator for Indian government schemes. Design concept: "the civic ledger" + 3D Scheme Mandala. See `design/DESIGN_CONSTITUTION.md`. |
| Research | `design/RESEARCH.md` — 5 references inspected 5 Nov 2026 (myScheme, CheckTenderAI, CSS 3D ring, GOV.UK writing, EligiCore). |
| Live application | NOT LIVE. Local only: http://127.0.0.1:8765 (verified by curl). Deploy planned: Render free web service — see `deployment/DEPLOYMENT_RUNBOOK.md`. |
| GitHub | NOT CREATED. Repo creation is the user's tap. Suggested: `github.com/MSAbhishek22/schemesathi`. No commit SHA yet. |
| Deployment | Provider: Render (planned, free). Build ID / timestamp: n/a. Manifest: `deployment/RELEASE_MANIFEST.json` (BLOCKED fields marked). |
| UI quality | Constitution + registry comparison vs CageCheck / Digest Room / Spec Ghost: UI_DISTINCTIVENESS PASS. No viewport screenshots yet (no browser in sandbox). |
| 3D experience | Scheme Mandala: CSS 3D ring, drag + keys + buttons, opt-in auto-turn, flat-button fallback under reduced motion. Code-verified; not yet opened in a browser. |
| Functional controls | `qa/INTERACTION_INVENTORY.md` — 30 controls inventoried; 24 PASS, 6 UNTESTED (need a real browser: drag, arrow keys, clipboard, viewports). No dead buttons by design; every control has a handler. |
| QA | `python3 -m unittest discover -s tests` → **25/25 PASS** (Linux, 5 Nov 2026). JS syntax: `node --check` OK. API smoke-tested with curl (`/health`, `/api/match`, `/api/whatif`, `GET /` 200, 34,238 bytes). |
| Demo video | NOT RECORDED. Must be recorded from the live URL after deploy (60–120s per rulebook; hackathon recommends 2–4 min). |
| Published video | BLOCKED (no live URL yet; no upload attempted). |
| Submission | Draft at `submission/SUBMISSION_DRAFT.md`. NOT registered, NOT submitted — user's taps. |

## Gate status
- GATE A — Research and design: **PASS** (5 refs, constitution, registry, 3D planned + built).
- GATE B — Functional product: **PASS** (all P0 features work via API; UI handlers code-verified).
- GATE C — 3D and visual quality: **PASS (code)** — Mandala implemented with fallback; browser visual check still UNTESTED.
- GATE D — QA: **PASS (Linux)** — 25/25 unit tests, API smoke tests, JS syntax. Browser E2E + viewports UNTESTED.
- GATE E — GitHub and deployment: **BLOCKED** — needs user's GitHub repo creation + Render free signup (no card; stop if asked).
- GATE F — Demo video: **BLOCKED** — needs live URL first.
- GATE G — Final handoff: **BLOCKED** — needs E + F, then user approval.

## Status summary
- `LIVE_DEPLOYMENT`: BLOCKED (no account created in this prep pass, per task rules).
- `GITHUB_COMMIT_MATCH`: BLOCKED (no repo yet).
- `ALL_VISIBLE_CONTROLS`: PASS (code) / UNTESTED (browser) — see inventory.
- `3D_EXPERIENCE`: PASS (code) / UNTESTED (browser visual).
- `UI_DISTINCTIVENESS`: PASS.
- `RESPONSIVE_AND_ACCESSIBLE`: FAIL (viewport screenshots + keyboard/focus test not yet run — honestly recorded, not claimed).
- `DEMO_VIDEO_RECORDED_FROM_LIVE`: BLOCKED.
- `VIDEO_PUBLISHED_AND_URL_VERIFIED`: BLOCKED.
- `HACKATHON_RULE_COMPLIANCE`: PASS (draft checklist in submission file; registration/submission are user taps).
- `OVERALL_RELEASE`: IN_PROGRESS.

## Known limitations
1. Scheme figures are a curated Nov 2026 snapshot — the app disclaims this
   and links every scheme to myscheme.gov.in for verification.
2. No browser E2E/viewport test yet — first open must be on the user's laptop.
3. The parser understands English/Hinglish keywords, not free-form
   semantics — it says NEEDS INFO rather than guessing when unsure.
4. Render free tier sleeps after inactivity (~60s cold start) — noted in
   the runbook and to be noted in the submission.
