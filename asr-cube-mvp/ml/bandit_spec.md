# Contextual Bandit Spec (Move Picker)

Arms: ["sideways","forward","down","up","reverse","still"]

Reward:
- applied → +1
- survived_to_export → +2
- quick_undo (<30s) → −1
- starred → +0.5

Features (per decision):
- tile: type, facet summary (small hash), staleness
- board: locked_count, empty_count, diversity_index
- user: spice (1–3), avg_undos, avg_time_to_apply
- heuristics: readability, coherence, novelty

Algo: Thompson Sampling (or LinUCB)
Persistence: JSON stats per arm per facet
