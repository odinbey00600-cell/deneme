from __future__ import annotations

import numpy as np

from .mini_rl_agent import ACTIONS, AgentConfig, MiniPolicyGradient


class StrategyAgent:
    def __init__(self, seed: int):
        self.agent = MiniPolicyGradient(AgentConfig(seed=seed))

    def choose_action(self, state: list[float]) -> str:
        s = np.array(state, dtype=np.float64)
        idx = self.agent.act(s)
        return ACTIONS[idx]

    def remember(self, state: list[float], action: str, reward: float):
        idx = ACTIONS.index(action)
        self.agent.remember(np.array(state, dtype=np.float64), idx, reward)

    def train_and_mutate(self) -> float:
        avg_ret = self.agent.train_episode()
        self.agent.mutate(scale=0.002)
        return avg_ret
