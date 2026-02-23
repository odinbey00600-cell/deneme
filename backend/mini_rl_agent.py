from __future__ import annotations

from dataclasses import dataclass
import io

import numpy as np


ACTIONS = ["OPEN_LONG", "OPEN_SHORT", "CLOSE_POSITION", "HOLD"]


@dataclass
class AgentConfig:
    state_dim: int = 10
    hidden1: int = 32
    hidden2: int = 32
    lr: float = 1e-3
    lr_decay: float = 0.995
    grad_clip: float = 1.0
    gamma: float = 0.99
    seed: int = 42


class MiniPolicyGradient:
    def __init__(self, cfg: AgentConfig):
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)
        self.w1 = self.rng.normal(0, 0.1, (cfg.state_dim, cfg.hidden1))
        self.b1 = np.zeros(cfg.hidden1)
        self.w2 = self.rng.normal(0, 0.1, (cfg.hidden1, cfg.hidden2))
        self.b2 = np.zeros(cfg.hidden2)
        self.w3 = self.rng.normal(0, 0.1, (cfg.hidden2, len(ACTIONS)))
        self.b3 = np.zeros(len(ACTIONS))
        self.episode: list[tuple[np.ndarray, int, float]] = []

    @staticmethod
    def _softmax(logits: np.ndarray) -> np.ndarray:
        x = logits - np.max(logits)
        exp_x = np.exp(x)
        return exp_x / np.sum(exp_x)

    def _forward(self, state: np.ndarray):
        h1 = np.tanh(state @ self.w1 + self.b1)
        h2 = np.tanh(h1 @ self.w2 + self.b2)
        logits = h2 @ self.w3 + self.b3
        probs = self._softmax(logits)
        return h1, h2, probs

    def act(self, state: np.ndarray) -> int:
        *_, probs = self._forward(state)
        return int(self.rng.choice(np.arange(len(ACTIONS)), p=probs))

    def remember(self, state: np.ndarray, action: int, reward: float) -> None:
        self.episode.append((state.copy(), action, reward))

    def train_episode(self) -> float:
        if not self.episode:
            return 0.0
        returns = []
        g = 0.0
        for _, _, r in reversed(self.episode):
            g = r + self.cfg.gamma * g
            returns.append(g)
        returns = np.array(list(reversed(returns)), dtype=np.float64)
        returns = (returns - returns.mean()) / (returns.std() + 1e-9)

        gw1 = np.zeros_like(self.w1)
        gb1 = np.zeros_like(self.b1)
        gw2 = np.zeros_like(self.w2)
        gb2 = np.zeros_like(self.b2)
        gw3 = np.zeros_like(self.w3)
        gb3 = np.zeros_like(self.b3)

        for (state, action, _), ret in zip(self.episode, returns):
            h1, h2, probs = self._forward(state)
            dlogits = probs
            dlogits[action] -= 1
            dlogits *= ret

            gw3 += np.outer(h2, dlogits)
            gb3 += dlogits
            dh2 = self.w3 @ dlogits
            dz2 = dh2 * (1 - h2**2)
            gw2 += np.outer(h1, dz2)
            gb2 += dz2
            dh1 = self.w2 @ dz2
            dz1 = dh1 * (1 - h1**2)
            gw1 += np.outer(state, dz1)
            gb1 += dz1

        for grad in [gw1, gb1, gw2, gb2, gw3, gb3]:
            np.clip(grad, -self.cfg.grad_clip, self.cfg.grad_clip, out=grad)

        self.w1 -= self.cfg.lr * gw1
        self.b1 -= self.cfg.lr * gb1
        self.w2 -= self.cfg.lr * gw2
        self.b2 -= self.cfg.lr * gb2
        self.w3 -= self.cfg.lr * gw3
        self.b3 -= self.cfg.lr * gb3
        self.cfg.lr *= self.cfg.lr_decay
        self.episode.clear()
        return float(returns.mean())

    def mutate(self, scale: float = 0.01):
        for w in [self.w1, self.w2, self.w3]:
            w += self.rng.normal(0, scale, w.shape)

    def serialize(self) -> bytes:
        buf = io.BytesIO()
        np.savez_compressed(
            buf,
            w1=self.w1,
            b1=self.b1,
            w2=self.w2,
            b2=self.b2,
            w3=self.w3,
            b3=self.b3,
            lr=np.array([self.cfg.lr]),
        )
        return buf.getvalue()
