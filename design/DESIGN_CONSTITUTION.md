# DESIGN CONSTITUTION — SchemeSathi

> Status: describes the **actual built UI** in `app/index.html` as of
> 5 Nov 2026. Where a feature is planned but unbuilt, it is marked so.

## 1. Product personality and emotional tone

A helpful clerk at a village service centre, not a government portal and
not a chatbot. Warm, plain-spoken, never bureaucratic. The product's job
is to remove fear: "am I even allowed to apply?" gets a straight answer,
in the user's own words, with the reason shown. No jargon, no legal
language, no dark patterns, no fake confidence — when it does not know
something, it says NEEDS INFO instead of guessing.

## 2. Target user and context of use

An Indian citizen — student, farmer, vendor, artisan, homemaker — trying
to find which government schemes they can actually use, usually on a
shared family phone or a low-end laptop, often with patchy connectivity.
The judge context is a laptop screen share: the whole answer (yours /
close / not yours + one rule trace) must be readable in one scroll.

## 3. Visual metaphor — the civic ledger / ration-card modernism

- **Ledger:** cream paper, ruled structure, stamped verdict chips. Every
  decision looks like an entry in a ledger: scheme name, verdict stamp,
  rule-by-rule account underneath.
- **Tricolour rule:** a 5px saffron–white–green bar at the very top — the
  only flag-waving in the product, restrained to one line.
- **Mandala:** the 8 scheme categories arranged as a 3D ring ("Scheme
  Mandala") — the citizen walks around the circle of what the state offers
  and stops at the category that matters.
- **No gradients, no glass, no glow.** Colour is flat and semantic.

## 4. Colour palette — semantic roles

| Token | Value | Role |
|---|---|---|
| Paper | `#FBF6EC` | Page background, ledger warmth |
| Card | `#FFFDF7` | Card surface |
| Ink | `#1E2420` | Primary text |
| Ink-soft | `#4A524C` | Secondary text |
| Green | `#14532D` | Primary actions, headings, ELIGIBLE |
| Green-deep | `#0E3B20` | Headings, dark accents |
| Green-soft | `#E4EFE6` | ELIGIBLE chip, privacy banner |
| Marigold | `#E8821A` | Focus rings, accents, Hindi subhead |
| Marigold-soft | `#FDF0DA` | Warm highlights |
| Line | `#D8CDB4` | Borders, ledger rules |
| Red | `#9B2C2C` | NOT ELIGIBLE |
| Amber | `#8A6D00` | CLOSE |
| Blue | `#1D4E89` | NEEDS INFO |

Verdict meaning is never colour-only: the word ELIGIBLE / CLOSE /
NEEDS INFO / NOT ELIGIBLE is always printed on the chip.

## 5. Typography

No webfonts, no CDN — the page renders from one HTML file served by the
stdlib server (same constraint as CageCheck, for the same reason: the demo
must work on a flaky connection).
- Headings: `Georgia, "Times New Roman", serif` — h1 40px, h2 20px, scheme
  names 17px. Serif gives the ledger/ gazette feel.
- Body: `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` 16px.
- Hindi subhead ("योजना साथी") in the same serif stack, marigold.
- Numbers (₹ amounts) use tabular-ish system rendering via
  `toLocaleString("en-IN")`.

## 6. Layout grid and page composition

Two-column app, `max-width: 1180px`, collapses to one column under 900px.
- Left column (380px): "1 · Tell us about yourself" — free-text box,
  example chips, primary action, parsed-profile receipt, structured form,
  situation checkboxes.
- Right column: "2 · Explore by category" (Mandala) → summary strip →
  verdict filter chips → scheme cards → "3 · What-if simulator".
- Footer: data-freshness + official-portal disclaimer.

## 7. Navigation and information architecture

One screen (`GET /`). No nav bar, no tabs, no routes. Filtering is by
category (Mandala / flat buttons) and by verdict (chips). Scheme cards
expand in place to show the rule trace, documents and steps. The what-if
simulator is a single section, not a separate page.

## 8. Component behaviour — as built

- **Free-text box:** plain textarea; Ctrl/Cmd+Enter submits; example
  chips fill it and run a check immediately.
- **Check my schemes:** POSTs to `/api/match`; button disables with
  "Checking schemes…" while the request is in flight (no duplicate
  submissions); on success the parsed profile is shown as a receipt and
  the form fields are filled from it for correction.
- **Parsed receipt:** shows exactly what the parser understood, with the
  note "Wrong or incomplete? Correct the boxes and check again."
- **Form fields:** age, income, gender, occupation, state, 19 situation
  checkboxes. Unticked = "not mentioned", never "no".
- **Mandala:** CSS 3D ring of 9 faces (All + 8 categories); prev/next
  buttons, drag (pointer events), arrow keys, opt-in auto-turn toggle;
  clicking a face filters results. Under `prefers-reduced-motion` the
  stage is hidden and a flat button list is shown instead.
- **Summary strip:** 4 counts (yours / close / need info / not yours).
- **Verdict filter chips:** filter the visible list; aria-pressed state.
- **Scheme cards:** click the header to expand; the trace lists every
  rule with ✓ / ✕ / ? and a plain-language "why"; CLOSE cards show a
  "What would change it" box; NEEDS INFO cards name the missing detail.
- **Copy checklist:** copies a plain-text checklist (name, benefit,
  verdict, documents, steps, official link) via clipboard; confirms with
  "✓ Copied!" for 1.8s.
- **What-if sliders:** income (0–₹20 lakh) and age (0–100); every change
  re-runs `/api/whatif` and updates the one-line result.
- **Error state:** a red banner appears only when the server cannot be
  reached, with the fix (`python3 run.py`).

## 9. Motion language

Restrained: 0.7s ease on the Mandala ring rotation only; card hover is a
background change, not movement. No auto-playing animation — auto-turn is
opt-in. `prefers-reduced-motion: reduce` kills the ring transition, hides
the 3D stage, and shows the flat category list.

## 10. 3D concept — the Scheme Mandala

- **Why 3D:** the 8 categories are a space to walk around, not a list to
  scroll. The ring makes "there is a whole circle of schemes, and you are
  standing at one of them" spatially legible in a way a dropdown is not.
- **Manipulation:** drag, ←/→ keys, prev/next buttons, click a face to
  filter, auto-turn toggle.
- **Fallback:** flat category buttons are always present in the DOM and
  are the *only* category control under reduced motion; every category is
  also reachable from the verdict filter + full list, so the ring is never
  the only path to a result.
- **Performance:** pure CSS 3D, 9 DOM faces, no WebGL, no library, no
  network asset. Mobile: stage is 230px tall, faces 132px wide, touch
  drag via pointer events.
- **Accessibility:** faces are real `<button>`s; the stage has an
  aria-label describing the controls; focus-visible outlines in marigold.

## 11. Responsive and accessibility — honest status

- Viewport meta present; two-column grid collapses at 900px; docs/steps
  grid collapses at 700px. **Viewport screenshots not yet taken** (no
  browser in this sandbox pass) — mobile/tablet check is recorded as
  UNTESTED in the release card, to be done on the user's laptop.
- All inputs have `<label>`s; checkboxes have text labels; buttons are
  native `<button>`s; focus-visible uses a 3px marigold outline.
- Contrast: ink on paper and green on cream are high by inspection; no
  measured WCAG ratio is claimed.
- Reduced motion: honoured (see §9–10).
- Language: `lang="en"`; Hindi appears only as scheme-name subtitles.

## 12. Original design decisions

- Ledger + Mandala instead of a dashboard: a citizen's question deserves
  a ledger entry, not a SaaS grid.
- Verdicts as plain words (yours / close / not yours) instead of scores:
  a score would fake precision; a rule trace is the evidence.
- NEEDS INFO as a first-class verdict: "unknown over a forced yes or no"
  is the product's honesty feature, borrowed from the governed-benefits
  pattern (see design/RESEARCH.md).
- No login, no storage, no tracking: the privacy banner is a feature,
  not a footnote — nothing typed ever leaves the machine.
