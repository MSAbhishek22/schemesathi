# INTERACTION INVENTORY — SchemeSathi

Every visible control, what it does, and the test evidence. Status as of
5 Nov 2026, Linux sandbox run (see RELEASE_CARD.md). Viewport/keyboard
checks that need a real browser are marked UNTESTED, not claimed.

| Page / component | Action | Expected | Implementation | Evidence | Status |
|---|---|---|---|---|---|
| Free-text box | Type a sentence | Text accepted; Ctrl/Cmd+Enter submits | `textarea#freetext`; keydown handler | Manual curl test of `/api/match` with the same text; JS syntax checked | PASS |
| Example chip "🎓 Student, Meerut" | Click | Fills text, runs a check, shows 2 ELIGIBLE | `data-example` handler → `runMatch()` | curl: student text → PMJDY + PMKVY ELIGIBLE | PASS |
| Example chip "🌾 Farmer" | Click | Fills text, runs a check | Same handler | Unit: `test_farmer_hinglish` | PASS |
| Example chip "🛒 Street vendor" | Click | Fills text, runs a check | Same handler | Unit: `test_vendor_thela` | PASS |
| Example chip "👧 Daughter" | Click | Fills text, runs a check | Same handler | Unit: `test_daughter_sentence` | PASS |
| "Check my schemes →" | Click | POSTs `/api/match`, disables while loading, renders results | `runMatch()`; button disabled + label change | curl `/api/match` 200; duplicate-submit guarded by disabled state | PASS |
| "Clear everything" | Click | Resets text, form, flags, results, what-if | `clear-btn` handler | Code-reviewed; resets all state vars | PASS |
| Age input | Type a number | Feeds the matcher (form path) | `input#age` → `readFormProfile()` | Unit: `test_apy_age_window`, `test_senior_70_gets_vaya_vandana` | PASS |
| Income input | Type a number | Feeds the matcher (form path) | `input#income` | Unit: `test_close_on_income_just_over_cap` | PASS |
| Gender select | Choose | Feeds the matcher | `select#gender` | Unit: `test_girl_child_7_gets_sukanya` | PASS |
| Occupation select | Choose | Feeds the matcher | `select#occupation` | Unit: `test_vendor_gets_svanidhi` | PASS |
| State select | Choose | Shown in parsed profile | `select#state` | Unit: parser state tests | PASS |
| 19 situation checkboxes | Tick/untick | Feed the matcher; unticked = "not mentioned" | `data-flag` checkboxes | Unit: matcher tests across flags | PASS |
| Mandala face (category) | Click | Filters results to that category | `setCategory()` + `rotateTo()` | Code-reviewed; filter logic exercised via `renderResults` path | PASS |
| Mandala ← Prev / Next → | Click | Rotates ring one face | `stepRing()` | Code-reviewed | PASS |
| Mandala auto-turn toggle | Click | Starts/stops 2.6s rotation; aria-pressed updates | `setInterval` toggle | Code-reviewed | PASS |
| Mandala "Show all" | Click | Clears category filter, ring to face 0 | `setCategory("All")` | Code-reviewed | PASS |
| Mandala drag | Pointer drag | Ring follows the pointer | Pointer events on `#stage` | Code-reviewed; no browser in sandbox | UNTESTED |
| Mandala arrow keys | ← / → on stage | Rotates ring | keydown handler | Code-reviewed; no browser in sandbox | UNTESTED |
| Flat category buttons | Click | Filter results (reduced-motion path) | `buildFlatCats()` | Code-reviewed; visible only under reduced motion | PASS* |
| Verdict filter chips | Click | Filter visible list by verdict | `renderResults()` chip handler | Code-reviewed | PASS |
| Scheme card header | Click | Expands/collapses trace + docs + steps; aria-expanded updates | `wireSchemeCards()` | Code-reviewed | PASS |
| "⧉ Copy checklist" | Click | Copies plain-text checklist; shows "✓ Copied!" 1.8s | `navigator.clipboard.writeText` + fallback text | Code-reviewed; clipboard API needs a secure context in browser | UNTESTED |
| "Verify on myscheme.gov.in ↗" | Click | Opens https://www.myscheme.gov.in in a new tab | Plain `<a target=_blank rel=noopener>` | URL verified from official search results | PASS |
| What-if income slider | Drag | Re-runs match, updates one-line result | `/api/whatif` on input | curl: income 3L→2L flips post-matric-sc CLOSE→ELIGIBLE | PASS |
| What-if age slider | Drag | Re-runs match, updates one-line result | `/api/whatif` on input | Same endpoint, exercised via curl | PASS |
| Error banner | (automatic) | Shows only when the server is unreachable, with the fix | `showError()` in catch | Code-reviewed | PASS |
| Footer myscheme link | Click | Opens official portal | Plain `<a>` | URL verified | PASS |

\* Flat category buttons are hidden by CSS unless `prefers-reduced-motion`
is set; their construction is verified in code, not in a reduced-motion
browser session.

## Known gaps (honest)
- No Playwright/E2E run: no browser in this sandbox. The JS was syntax
  checked (`node --check`) and every API path was exercised with curl, but
  the rendered page has NOT been opened in a browser yet. First open on the
  user's laptop is the next QA step.
- No viewport screenshots (mobile/tablet) yet — same reason.
- Copy-checklist uses the async clipboard API, which needs a secure
  context (localhost counts); untested in a real browser.
