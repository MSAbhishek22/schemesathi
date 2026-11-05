# DESIGN RESEARCH — SchemeSathi (SLAY HACKS 2026)

Inspected 5 Nov 2026 (search-result level + official pages opened where noted).
Honest status: references 1–2 were inspected via the official pages/search
results returned by the browser; references 3–5 via search-result extracts.
No reference is claimed as fully read where only an extract was returned.

## 1. Same-category reference — myScheme.gov.in (official GoI portal)
- URL: https://www.myscheme.gov.in (About page opened via search result)
- Inspected: About/FAQ extracts — one-stop search & discovery of 4,700+
  central + state schemes; 3-step flow (enter details → see matches →
  scheme page); eligibility questionnaire with Yes/No questions; 15 categories.
- Worth learning: category taxonomy (we reuse its 8 overlapping categories);
  the "check eligibility" questionnaire pattern; linking every scheme to an
  official apply page.
- Do NOT copy: the structured-form-only intake (our differentiator is plain
  language); the login-gated saved profile (we are login-free, on-device);
  the match-only list with no explanation (we add rule traces + near-miss).
- Translation: our category set and "verify on the official portal" link
  come from here; our differentiator (why / why-not / what-if) is the gap
  myScheme leaves open.

## 2. Same-category reference — CheckTenderAI (eligibility checker, India)
- URL: https://www.checktenderai.com/ (search-result extract)
- Inspected: "AI extracts eligibility clauses; the final eligibility decision
  is deterministic and rule-based — consistent, explainable results."
- Worth learning: the explicit separation — AI for extraction, rules for the
  decision. That is exactly our neurosymbolic split (NLP parses, rules decide).
- Do NOT copy: tender-specific domain; PDF upload flow.
- Translation: our submission text states the same boundary in plain words.

## 3. Interaction/motion reference — CSS 3D ring carousels
- URLs: https://raw.org/software/graphics/introduction-to-css-3d-transforms/,
  https://movingparts.supply/components/ring-carousel/ (search-result extracts)
- Inspected: ring built from `rotateY(i*360/n) translateZ(radius)`; drag with
  pointer events + friction; "under reduced motion the ring stands still and
  every input steps one card at once"; "do not encode essential state solely
  through depth or motion — maintain text, focus and non-3D fallbacks."
- Worth learning: the ring as a cyclic gallery; keyboard stepping; the
  reduced-motion contract.
- Do NOT copy: inertia/friction physics (overkill); auto-rotation by default.
- Translation: our Scheme Mandala is a CSS 3D ring of the 8 categories with
  prev/next buttons, drag, arrow keys, an opt-in auto-turn, and a flat
  button list that replaces it entirely under reduced motion.

## 4. Typography / hierarchy reference — GOV.UK Service Manual, "Writing for UIs"
- URL: https://www.gov.uk/service-manual/design/writing-for-user-interfaces
  (search-result extract)
- Inspected: "minimise cognitive load… using the same language as your users";
  "ask questions to establish eligibility rather than putting a long list of
  eligibility conditions on the start page"; one idea per sentence; headings
  describe the purpose of the text below them.
- Worth learning: eligibility-as-questions, plain language, reading age 9.
- Do NOT copy: GOV.UK's visual system itself (different country, different
  brand; we need our own identity).
- Translation: our copy is short sentences, first-person intake ("Tell us
  about yourself"), verdicts as plain words (yours / close / not yours),
  and rule traces written as "Family income up to ₹2,50,000 a year — Your
  income: ₹3,00,000".

## 5. 3D / spatial reference — EligiCore dossier (explainable eligibility)
- URL: https://github.com/lakshya172/eligicore/blob/HEAD/EligiCore_Dossier_update.md
  (search-result extract)
- Inspected: "eligibility-first… explains exactly why"; "hard rules before AI";
  "These three you're borderline on — check with the company. These you don't
  qualify for, and here's the specific reason."
- Worth learning: the three-bucket presentation (qualify / borderline / don't)
  maps directly onto our ELIGIBLE / CLOSE / NOT ELIGIBLE buckets; the
  "explainable rule-plus-AI" framing.
- Do NOT copy: job-domain rules; API-first shape; spreadsheet export.
- Translation: our summary strip (yours / close / need info / not yours) and
  the CLOSE bucket's "what would change it" advice.

## Related work noted (not a design reference)
- EligiCore targets job eligibility for students; SchemeSathi targets Indian
  government schemes for citizens — different domain, same explainability
  principle. Cited here so the originality claim stays honest.
