# SchemeSathi — Which sarkari schemes are actually yours?

**SLAY HACKS 2026** · solo · fresh build · free-only · on-device
Also entered in **GenHacks** (submitted 12 Nov 2026).
Live: **https://schemesathi-kappa.vercel.app** · Repo: https://github.com/MSAbhishek22/schemesathi ·
Demo video: https://www.youtube.com/watch?v=e0H6pNcQEhs

Describe your life in one sentence — in English or Hinglish — and
SchemeSathi checks **18 real Indian government schemes** rule by rule and
tells you which ones are yours, which ones you're close to, and *exactly
why* for every one you're not. With the documents, the steps, and a
what-if simulator that shows what would change the answer.

## The gap it fills

The official portal (myscheme.gov.in) already lists 4,700+ schemes. But:
1. You have to speak the portal's language (structured forms), not yours.
2. You only see what you match — a "no" comes with no reason.
3. Applying is a second maze of documents and ministry sites.

SchemeSathi answers in your words, explains every no, and hands you the
checklist for the yeses. Nothing is uploaded, no account, no login.

## How it works (honest AI)

Neurosymbolic, on-device — no cloud model, no API key:
1. **NLP layer** parses plain English/Hinglish into a profile (age, income,
   gender, occupation, state, life situation; lakh/crore and monthly figures
   normalised).
2. **Symbolic rules engine** evaluates every scheme deterministically and
   returns a per-rule trace. Verdicts: `ELIGIBLE` / `CLOSE` / `NOT ELIGIBLE`
   / `NEEDS INFO`. Unknown is a real answer, never a guessed yes/no.

## Features

- Plain-language intake + structured form (correct anything it understood)
- 4 example personas (student / farmer / street vendor / daughter)
- Rule-by-rule verdict traces; CLOSE schemes explain what would change it
- What-if simulator (income + age sliders, live re-match)
- Document checklists + application steps + one-click copy
- **3D Scheme Mandala** — the 8 categories as a draggable CSS-3D ring,
  with a flat button list as the reduced-motion fallback
- Fully offline-capable: no CDN, no webfonts, no external assets

## Run it

```bash
python3 run.py          # serves http://127.0.0.1:8765
```

Python 3.10+ stdlib only — no install step. Set `SCHEMESATHI_PORT` to
change the port.

## Tests

```bash
python3 -m pytest tests/ -q
```

42 tests, all passing (re-verified 13 Nov 2026): parser (incl. the
"school must not trigger the SC flag" and "70000 must not trigger
senior70" traps), matcher (eligible / close / hard-no / needs-info),
what-if flips, trace completeness, and the frontend/Vercel entrypoint
and routing suites. (25 of the tests also run under plain
`python3 -m unittest discover -s tests`; the remaining modules import
pytest.)

## Data honesty

Scheme figures are a **curated snapshot as of November 2026** — benefit
amounts, income caps and age windows change. The app says so on every
screen and links every scheme to the official portal
(https://www.myscheme.gov.in) for verification before applying.
SchemeSathi is an independent demo, not a government service; its verdicts
are guidance, not an official eligibility decision.

## Status

`IN_PROGRESS` under the ABHI_22 rulebook — Gates A–D pass (research,
design, working product, QA on Linux). Gate E passed on Vercel (not
Render): **live at https://schemesathi-kappa.vercel.app**, verified
13 Nov 2026. Gate F passed: the demo video
(https://www.youtube.com/watch?v=e0H6pNcQEhs) was recorded from the
live URL. Submitted to SLAY HACKS 2026 on 7 Nov 2026 and to GenHacks
on 12 Nov 2026. See `RELEASE_CARD.md` for the full gate table.
