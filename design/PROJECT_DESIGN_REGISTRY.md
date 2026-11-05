# Project Design Registry — SchemeSathi (SLAY HACKS 2026)

Comparison vs the three most recent rulebook-era projects, from their
recorded design constitutions (previous project screenshots were not on
file for inspection — noted honestly).

## This project
- Concept: "The civic ledger" — cream paper, ruled structure, stamped
  verdict chips; the 8 scheme categories as a 3D ring ("Scheme Mandala").
- Palette: cream paper `#FBF6EC` + deep government green `#14532D` +
  marigold `#E8821A`, with a 5px saffron–white–green tricolour rule.
- Type: Georgia serif headings (ledger/gazette feel) + system sans body;
  Hindi subtitles in marigold.
- Layout: two-column app — intake form left (380px), Mandala + results
  right; collapses to one column under 900px.
- Signature interaction: plain-language sentence → parsed-profile receipt
  → rule-by-rule verdict trace → what-if sliders.
- 3D: CSS 3D ring of categories, draggable, keyboard-steppable, with a
  flat button list as the reduced-motion fallback.

## Compared projects
1. CageCheck (Vultr, 3 Nov) — paper/ink/stamp, light paper background,
   single 720px column, mono receipts, deterministic guard UI.
   DIFFERENCE: SchemeSathi is a two-column citizen app, not a single-column
   guard tool; green + marigold civic palette, not ink-only; serif ledger
   headings + a 3D ring, not a stamp + receipt; the interaction is
   conversation → trace, not paste → stamp. No stamp, no cage, no mono
   receipt slip.
2. Digest Room (Flip the Switch, 5 Nov) — dark console, deep slate +
   signal lime, three-column room layout (room list | timeline | tasks rail).
   DIFFERENCE: SchemeSathi is light, warm and paper-based, not dark; two
   columns, not three; no chat timeline, no lime agent voice, no task rail.
3. Spec Ghost (Kiroween, 3 Nov) — near-black brown + candlelight amber,
   Georgia serif, 860px single column, candlelit document feel.
   DIFFERENCE: SchemeSathi shares Georgia serif (a system font, not a
   copied identity) but is light cream + green, two-column, with a marigold
   accent and a 3D ring — not a dark single-column document. The serif is
   used for ledger headings, not candlelit prose.

Verdict: recognisably different in concept, palette, layout, interaction
and motion. UI_DISTINCTIVENESS: PASS.
