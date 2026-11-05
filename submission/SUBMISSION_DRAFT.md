# SLAY HACKS 2026 — SUBMISSION DRAFT (SchemeSathi)

> DRAFT ONLY — NOT SUBMITTED. Devpost registration + submission are the
> user's own taps. Video must be recorded from the live URL after deploy.
> Do not paste this into Devpost until the live URL + video exist.

## Project name
**SchemeSathi — Which sarkari schemes are actually yours?**
(योजना साथी)

## Tagline
Describe your life in one sentence. Get every government scheme you qualify
for — and the exact reason for every one you don't.

## Problem
India has 4,700+ government schemes, and the official portal (myScheme)
already lists them. But citizens still don't use them, for three reasons:
1. **You have to speak the portal's language**, not yours — structured forms,
   not "I'm a 19-year-old student from Meerut, family income 2 lakh."
2. **You only ever see what you match.** A "no" comes with no reason, so
   people never learn they were one document — or ₹50,000 of income — away.
3. **Applying is a second maze** — documents, steps, and the right portal
   are scattered across ministry sites.

## Solution
SchemeSathi is a fully on-device, login-free navigator:
- **Plain-language understanding:** type a sentence in English or Hinglish;
  a local NLP parser reads age, income, gender, occupation, state and life
  situation (farmer, vendor, artisan, girl child, kutcha house…).
- **Explainable matching:** a deterministic rules engine checks 18 real
  schemes rule by rule and returns a per-rule trace. Every verdict is
  ELIGIBLE / CLOSE / NOT ELIGIBLE / NEEDS INFO — and "unknown" is a real
  answer, never a guessed yes or no.
- **Near-miss intelligence:** CLOSE schemes explain exactly what would
  change the answer, and a what-if simulator lets you move income and age
  sliders to see what opens up.
- **The last mile:** every scheme card lists the exact documents, the
  step-by-step application path, a one-click copyable checklist, and a link
  to verify on the official portal.
- **3D Scheme Mandala:** the 8 scheme categories as a draggable CSS-3D
  ring — walk around what the state offers, stop at your category. Full
  flat-button fallback under reduced motion.

## AI implementation (honest)
Neurosymbolic, on-device — no cloud model, no API key, no data leaves the
machine. The NLP layer (keyword/entity extraction, Hinglish handling,
lakh/crore and monthly-to-annual normalisation) *understands* the sentence;
the symbolic rules engine *decides* eligibility. The decision is never
generated prose: it is always the published rules, shown as a trace. This
separation follows the governed-benefits pattern — a language model may
interpret a question, but its wording must never become the source of an
entitlement decision.

## Tech
Python 3 stdlib only (no dependencies, no install step). `http.server`
serves the single-page UI and a JSON API (`/api/match`, `/api/whatif`).
CSS 3D for the Mandala. 25 unit tests (parser + matcher + traces).

## Links (TO FILL after user taps)
- Live app URL: _PENDING — Render free deploy (user's Render signup)_
- GitHub repo: _PENDING — repo creation is the user's tap_
- Demo video (2–4 min, recorded from the live URL): _PENDING_
- Screenshots: _take from the live URL, not from localhost_

## Team
Solo — M S Abhishek (Shobhit University, Meerut, India).

## Rule-compliance checklist
- [x] Original work, built fresh for SLAY HACKS (scaffold started 5 Nov 2026
      as prep, two days before the event's Nov 7 start; the build continues
      into the event window. No code copied from CageCheck or any prior
      project — new codebase, new design, new domain).
- [x] Meaningful AI use (NLP + explainable rules engine).
- [x] Working prototype with a live demo path (deploy pending).
- [x] No plagiarism; scheme facts are a labelled snapshot, verified against
      the official portal, with a disclaimer in-app and in the README.
- [x] Free-only: no paid service, no card, no account anywhere in the build.
- [ ] Devpost registration + submission — USER'S TAP.
- [ ] Live HTTPS deployment — BLOCKED on user's Render signup (free tier).
- [ ] Demo video from the live URL — BLOCKED on deployment.
- [ ] GitHub repo — PENDING user's tap.

## Prizes aimed at
Grand Prize $2,000 / Runner-Up $1,200 / 3rd $800. NOTE: Best Beginner Hack
($500) is for first-time hackathon participants — the user is NOT a
first-time participant, so that category is NOT claimed.
