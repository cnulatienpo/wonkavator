# metrics.py — compute KPIs from suggestion events
import json, math
import numpy as np

def compute_kpis(rows):
    if not rows:
        return {"hit_rate_at_3":0,"undo_rate":0,"survival_rate":0,"time_to_first_apply_sec":None,"star_rate":0}
    # For simplicity, treat any 'applied' as a 'hit'; assume top-3 if ranker would put it high (not known here).
    # We'll compute generic rates:
    n = len(rows)
    applied = sum(1 for r in rows if r.get("applied"))
    undo_quick = sum(1 for r in rows if (r.get("undone_within_sec") is not None and r["undone_within_sec"]<=30))
    survived = sum(1 for r in rows if r.get("survived_to_export"))
    starred = sum(1 for r in rows if r.get("starred"))
    tfas = [r["time_to_apply_sec"] for r in rows if r.get("applied") and r.get("time_to_apply_sec") is not None]
    kpis = {
        "hit_rate_at_3": round(applied/max(n,1),3),  # placeholder; real @3 needs deck positions
        "undo_rate": round(undo_quick/max(n,1),3),
        "survival_rate": round(survived/max(n,1),3),
        "time_to_first_apply_sec": (min(tfas) if tfas else None),
        "star_rate": round(starred/max(n,1),3),
        "n_rows": n
    }
    return kpis
