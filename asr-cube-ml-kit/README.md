# ASR Cube — ML Kit (Move Picker + Deck Ranker)

**Date:** 2025-11-02

This kit gives you a *working*, local-only training pipeline to make the Cube smarter **without any cloud AI**.
It updates two tiny models:
- **Bandit** (LinUCB) → picks which move to try next (sideways/forward/down/up/reverse/still)
- **Ranker** (logistic regression) → sorts a suggestion deck best→worst for the user/context

## Files
- `train.py` — Run this. It loads logs from `samples/events.jsonl` (or your path), trains/updates, then writes:
  - `models/bandit.json`
  - `models/ranker.npz` (weights) + `models/feature_meta.json`
  - `reports/metrics.json` + `reports/metrics.md`
- `feature_extractor.py` — Turns suggestion events into feature vectors
- `bandit.py` — LinUCB contextual bandit (small & fast)
- `ranker.py` — Numpy logistic regression with L2
- `metrics.py` — Computes KPIs you care about
- `schemas/events_suggestion.schema.json` — Expected JSONL row shape
- `samples/events.jsonl` — Tiny mock session you can train on immediately

## Expected log format (JSONL)
One row per **suggestion shown** with outcomes:
- `suggestion_id` (string)
- `user_id` (string)
- `tile_type` (string) — e.g., "image","audio","concept","mood"
- `move` (string) — one of "sideways","forward","down","up","reverse","still"
- `intensity` (int 1..3)
- `spice` (int 1..3)
- `time_budget_sec` (int)
- `shown_at` (ISO timestamp)
- Outcomes:
  - `applied` (bool)
  - `undone_within_sec` (number | null)
  - `starred` (bool)
  - `survived_to_export` (bool)
  - `time_to_apply_sec` (number | null)

## Running
```
python3 train.py --logs samples/events.jsonl
```

Models + metrics are written under `models/` and `reports//`.
Swap in your own JSONL later and rerun. The kit will update (not crash) if features change.
