# Suggestion Ranker Spec (Deck Sorter)

Model: Gradient-boosted trees or small ONNX
Target: clicked/applied (binary), secondary = undo

Features:
- embedding sims (tile↔user style, tile↔suggestion text)
- heuristics (readability, coherence, novelty)
- move + intensity one-hots
- risk/spice
- time budget match

Metrics:
- Hit-rate@3 (↑)
- Undo rate (↓)
- Time-to-first-apply (↓)
- Survival-to-export (↑)
