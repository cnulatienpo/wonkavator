# bandit.py — LinUCB contextual bandit
import json
import numpy as np

class LinUCB:
    def __init__(self, n_arms:int, ctx_dim:int, alpha:float=0.8):
        self.n_arms = n_arms
        self.ctx_dim = ctx_dim
        self.alpha = alpha
        # Per-arm A (dxd) and b (dx1)
        self.A = [np.eye(ctx_dim) for _ in range(n_arms)]
        self.b = [np.zeros((ctx_dim,1)) for _ in range(n_arms)]

    def select(self, ctx: np.ndarray):
        # ctx: (d,)
        ctx = ctx.reshape(-1,1)
        best_arm, best_ucb = 0, -1e9
        for a in range(self.n_arms):
            A_inv = np.linalg.inv(self.A[a])
            theta = A_inv @ self.b[a]
            mu = float((theta.T @ ctx)[0,0])
            sigma = float(np.sqrt(ctx.T @ A_inv @ ctx))
            ucb = mu + self.alpha * sigma
            if ucb > best_ucb:
                best_ucb, best_arm = ucb, a
        return best_arm

    def update(self, arm:int, ctx: np.ndarray, reward: float):
        ctx = ctx.reshape(-1,1)
        self.A[arm] += ctx @ ctx.T
        self.b[arm] += reward * ctx

    def to_json(self):
        return {
            "n_arms": self.n_arms,
            "ctx_dim": self.ctx_dim,
            "alpha": self.alpha,
            "A": [A.tolist() for A in self.A],
            "b": [b.tolist() for b in self.b],
        }

    @staticmethod
    def from_json(obj):
        n_arms = obj["n_arms"]; ctx_dim = obj["ctx_dim"]; alpha = obj.get("alpha",0.8)
        bandit = LinUCB(n_arms, ctx_dim, alpha)
        bandit.A = [np.array(A) for A in obj["A"]]
        bandit.b = [np.array(b) for b in obj["b"]]
        return bandit
