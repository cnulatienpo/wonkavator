# feature_extractor.py
import json, math
import numpy as np
from collections import defaultdict

MOVES = ["sideways","forward","down","up","reverse","still"]

def one_hot(value, choices):
    vec = np.zeros(len(choices), dtype=float)
    if value in choices:
        vec[choices.index(value)] = 1.0
    return vec

def build_features(rows):
    r"""
    Turn suggestion rows into (X, y_click, rewards, ctx_for_bandit, arms).
      - X: feature matrix for ranker
      - y_click: binary label (applied as proxy for click)
      - rewards: shaped reward for bandit (applied + starred + survived - quick undo)
      - ctx_for_bandit: context vector (tile_type/ intensity/ spice / time budget scaled)
      - arms: index of move (0..5)
    r"""
    tile_types = sorted({r["tile_type"] for r in rows})
    feats = []
    labels = []
    rewards = []
    ctxs = []
    arms = []
    for r in rows:
        # core categorical
        f_move = one_hot(r["move"], MOVES)  # ranker sees move too
        f_tile = one_hot(r["tile_type"], tile_types)
        # scaled numerics
        intensity = (r.get("intensity",1)-1)/2.0  # 0..1
        spice = (r.get("spice",1)-1)/2.0         # 0..1
        tb = min(r.get("time_budget_sec",0)/1800.0, 1.0)  # <= 30min scaled
        # interactions (simple)
        inter = np.array([intensity*spice, spice*tb, intensity*tb], dtype=float)
        x = np.concatenate([f_move, f_tile, [intensity, spice, tb], inter])
        feats.append(x)
        # labels and rewards
        applied = 1.0 if r.get("applied") else 0.0
        labels.append(applied)
        reward = 0.0
        reward += 1.0 if r.get("applied") else 0.0
        reward += 0.5 if r.get("starred") else 0.0
        reward += 2.0 if r.get("survived_to_export") else 0.0
        undo = r.get("undone_within_sec")
        if undo is not None and undo <= 30: reward -= 1.0
        rewards.append(reward)
        # bandit context (exclude move one-hot; move becomes the arm)
        ctx = np.concatenate([f_tile, [intensity, spice, tb], inter])
        ctxs.append(ctx)
        arms.append(MOVES.index(r["move"]))
    X = np.vstack(feats) if feats else np.zeros((0,1))
    y = np.array(labels, dtype=float)
    R = np.array(rewards, dtype=float)
    C = np.vstack(ctxs) if ctxs else np.zeros((0,1))
    A = np.array(arms, dtype=int)
    meta = {"tile_types": tile_types, "moves": MOVES, "ranker_dim": int(X.shape[1]), "ctx_dim": int(C.shape[1])}
    return X, y, R, C, A, meta
