from __future__ import annotations

import math
import random
from collections import deque
from dataclasses import dataclass


ACTIONS = ['OPEN_LONG', 'OPEN_SHORT', 'CLOSE_POSITION', 'HOLD']


@dataclass
class Experience:
    state: list[float]
    action: int
    reward: float
    next_state: list[float]
    done: bool


class RLAgent:
    def __init__(self, seed: int, learning_rate: float = 0.01, gamma: float = 0.99) -> None:
        self.rng = random.Random(seed)
        self.epsilon = 0.2
        self.lr = learning_rate
        self.gamma = gamma
        self.q_table: dict[tuple[int, ...], list[float]] = {}
        self.buffer: deque[Experience] = deque(maxlen=5000)

    def _bucketize(self, state: list[float]) -> tuple[int, ...]:
        return tuple(int(math.tanh(x) * 10) for x in state)

    def act(self, state: list[float]) -> str:
        key = self._bucketize(state)
        if key not in self.q_table:
            self.q_table[key] = [0.0] * len(ACTIONS)
        if self.rng.random() < self.epsilon:
            return self.rng.choice(ACTIONS)
        best = max(range(len(ACTIONS)), key=lambda i: self.q_table[key][i])
        return ACTIONS[best]

    def store(self, exp: Experience) -> None:
        self.buffer.append(exp)

    def train_step(self, batch_size: int = 32) -> None:
        if len(self.buffer) < batch_size:
            return
        batch = self.rng.sample(list(self.buffer), batch_size)
        for exp in batch:
            key = self._bucketize(exp.state)
            nxt = self._bucketize(exp.next_state)
            self.q_table.setdefault(key, [0.0] * len(ACTIONS))
            self.q_table.setdefault(nxt, [0.0] * len(ACTIONS))
            q = self.q_table[key][exp.action]
            target = exp.reward + (0 if exp.done else self.gamma * max(self.q_table[nxt]))
            td = max(min(target - q, 5.0), -5.0)
            self.q_table[key][exp.action] += self.lr * td
        self.epsilon = max(0.02, self.epsilon * 0.999)
        self.lr = max(0.0001, self.lr * 0.99995)
