from __future__ import annotations

import random
from collections import defaultdict


class TimingRLAgent:
    """Lightweight state-action learner: 0 hold, 1 enter, 2 exit."""

    def __init__(self) -> None:
        self.q = defaultdict(lambda: [0.0, 0.0, 0.0])
        self.epsilon = 0.15
        self.alpha = 0.1
        self.gamma = 0.95

    def _state_key(self, state: dict[str, float]) -> tuple[int, int, int]:
        return (
            int(state["regime"]),
            int(state["rsi"] // 10),
            int(state["volatility"] * 1000),
        )

    def act(self, state: dict[str, float]) -> int:
        key = self._state_key(state)
        if random.random() < self.epsilon:
            return random.randint(0, 2)
        values = self.q[key]
        return int(max(range(3), key=lambda i: values[i]))

    def learn(self, s: dict[str, float], a: int, reward: float, s2: dict[str, float]) -> None:
        k1 = self._state_key(s)
        k2 = self._state_key(s2)
        best_next = max(self.q[k2])
        self.q[k1][a] += self.alpha * (reward + self.gamma * best_next - self.q[k1][a])
