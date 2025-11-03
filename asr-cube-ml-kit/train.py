# train.py — end-to-end updater for Bandit + Ranker
import json, argparse, os
import numpy as np
from feature_extractor import build_features
from bandit import LinUCB
from ranker import LogisticRanker
from metrics import compute_kpis

def load_jsonl(path):
    rows = []
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            rows.append(json.loads(line))
    return rows

def save_json(obj, path):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(obj,f,indent=2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", required=True, help="Path to suggestion events JSONL")
    ap.add_argument("--models_dir", default="models")
    ap.add_argument("--reports_dir", default="reports")
    args = ap.parse_args()

    rows = load_jsonl(args.logs)
    X, y, R, C, A, meta = build_features(rows)

    # --- Bandit ---
    bandit_path = os.path.join(args.models_dir, "bandit.json")
    if os.path.exists(bandit_path):
        bandit = LinUCB.from_json(json.load(open(bandit_path,"r",encoding="utf-8")))
    else:
        bandit = LinUCB(n_arms=len(meta["moves"]), ctx_dim=meta["ctx_dim"], alpha=0.8)

    # update bandit with observed rewards
    for i in range(len(rows)):
        bandit.update(arm=A[i], ctx=C[i], reward=float(R[i]))

    os.makedirs(args.models_dir, exist_ok=True)
    save_json(bandit.to_json(), bandit_path)

    # --- Ranker ---
    ranker = LogisticRanker(dim=int(meta["ranker_dim"]), lr=0.2, l2=1e-3, iters=800)
    ranker.fit(X, y)
    ranker.to_npz(os.path.join(args.models_dir, "ranker.npz"), meta=meta)
    with open(os.path.join(args.models_dir,"feature_meta.json"),"w",encoding="utf-8") as f:
        json.dump(meta,f,indent=2)

    # --- Metrics ---
    kpis = compute_kpis(rows)
    os.makedirs(args.reports_dir, exist_ok=True)
    with open(os.path.join(args.reports_dir,"metrics.json"),"w",encoding="utf-8") as f:
        json.dump(kpis,f,indent=2)
    with open(os.path.join(args.reports_dir,"metrics.md"),"w",encoding="utf-8") as f:
        f.write("# ASR Cube — Training Metrics\n\n")
        for k,v in kpis.items():
            f.write(f"- **{k}**: {v}\n")

    print("Saved models to", args.models_dir)
    print("Metrics:", json.dumps(kpis))

if __name__ == "__main__":
    main()
