# ranker.py — simple logistic regression with numpy
import json, math
import numpy as np

class LogisticRanker:
    def __init__(self, dim:int, lr:float=0.1, l2:float=1e-3, iters:int=500):
        self.dim = dim
        self.lr = lr
        self.l2 = l2
        self.iters = iters
        self.w = np.zeros(dim, dtype=float)

    def fit(self, X: np.ndarray, y: np.ndarray):
        if X.shape[0] == 0:
            return
        w = self.w.copy()
        for _ in range(self.iters):
            z = X @ w
            p = 1.0 / (1.0 + np.exp(-z))
            grad = X.T @ (p - y) / X.shape[0] + self.l2 * w
            w -= self.lr * grad
        self.w = w

    def predict_proba(self, X: np.ndarray):
        z = X @ self.w
        return 1.0 / (1.0 + np.exp(-z))

    def to_npz(self, path:str, meta:dict):
        np.savez(path, w=self.w, meta=json.dumps(meta))

    @staticmethod
    def from_npz(path:str):
        data = np.load(path, allow_pickle=True)
        w = data["w"]
        meta = json.loads(str(data["meta"]))
        lr = LogisticRanker(dim=w.shape[0])
        lr.w = w
        return lr, meta
