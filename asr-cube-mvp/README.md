# ASR Cube — MVP Starter Bundle

**Date:** 2025-11-02

This bundle contains schemas, registries, sample data, and specs so you can start building the Rubik's‑style Cube app **without AI**. It encodes the *moves engine*, *type registry*, *oracle outputs*, and *event log* you asked for.

Everything is local-first and file-based. You can open/edit any JSON and wire it into your stack.

## What’s inside

- `schemas/`
  - `tile_envelope.schema.json` – Typed Tile envelope + common facets
  - `events_schema.json` – Event log rows for apply/undo/branch
  - `move_registry.json` – Move→modifiers recipes per facet
  - `type_registry.json` – Filetype adapters (detect/preview/ops/exporters)
  - `deliverables_registry.json` – Simple "no-fancy" deliverables (poster/video/pack)
- `ui-copy/`
  - `oracle_lines_pantry.json` – The long, titled lines for your pantry example
  - `strings.json` – Button labels and small UI strings
- `data/`
  - `example_board.asrboard.json` – A tiny sample board with tiles
  - `shake_cards_examples.json` – Example Shake cards (imperatives, questions, what‑ifs)
- `ml/`
  - `bandit_spec.md` – Contextual bandit: arms, rewards, features
  - `ranker_spec.md` – Suggestion ranker: features, metrics, training rows
- `backend/`
  - `pipelines_spec.md` – Deterministic media ops and job graph examples

## Suggested build order

1. Load `schemas/tile_envelope.schema.json` and `schemas/events_schema.json`
2. Hard‑code `schemas/move_registry.json` and `schemas/type_registry.json`
3. Render the Cube + Drawer and **wire only these**:
   - "You could do this:" / "I wonder," / "What if" buttons → `ui-copy/oracle_lines_pantry.json`
   - Global/Per‑tile Shake → `data/shake_cards_examples.json`
4. Apply = append an event in `data/example_board.asrboard.json` (no real processing needed day‑1)
5. Save/Load = read/write `*.asrboard.json`

Keep it small. You can bolt on DeepSeek later to phrase oracle lines—**the move selection remains yours**.
