from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class ReplayState:
    enabled: bool = False
    seed: int = 42
    cursor: int = 0


class ReplayController:
    def __init__(self, seed: int = 42):
        self.state = ReplayState(seed=seed)
        self.rng = random.Random(seed)

    def toggle(self, enabled: bool, seed: int | None = None) -> ReplayState:
        self.state.enabled = enabled
        if seed is not None:
            self.state.seed = seed
            self.rng.seed(seed)
            self.state.cursor = 0
        return self.state

    def next_index(self, total: int) -> int:
        if total == 0:
            return 0
        if self.state.enabled:
            idx = self.state.cursor % total
            self.state.cursor += 1
            return idx
        return total - 1
