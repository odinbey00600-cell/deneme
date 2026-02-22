from __future__ import annotations

from dataclasses import dataclass

import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces


@dataclass
class PositionState:
    side: int = 0  # -1 short, 0 flat, +1 long
    entry_price: float = 0.0


class FuturesTimingEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, df: pd.DataFrame) -> None:
        super().__init__()
        self.df = df.reset_index(drop=True)
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=-10, high=10, shape=(8,), dtype=np.float32)
        self.step_idx = 30
        self.position = PositionState()
        self.last_equity = 0.0
        self.trade_count = 0

    def _obs(self) -> np.ndarray:
        row = self.df.iloc[self.step_idx]
        return np.array(
            [
                row["ema_spread_fast"],
                row["ema_spread_swing"],
                row["rsi14"] / 100.0,
                row["atr14"] / row["close"],
                row["vwap_dev"],
                row["returns_3"],
                float(self.position.side),
                self.last_equity,
            ],
            dtype=np.float32,
        )

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self.step_idx = 30
        self.position = PositionState()
        self.last_equity = 0.0
        self.trade_count = 0
        return self._obs(), {}

    def step(self, action: int):
        price = self.df.iloc[self.step_idx]["close"]
        next_price = self.df.iloc[self.step_idx + 1]["close"]

        reward = 0.0
        if action == 1 and self.position.side == 0:
            self.position = PositionState(side=1, entry_price=price)
            self.trade_count += 1
        elif action == 2 and self.position.side == 0:
            self.position = PositionState(side=-1, entry_price=price)
            self.trade_count += 1
        elif action == 3 and self.position.side != 0:
            pnl = (price - self.position.entry_price) * self.position.side
            reward += pnl
            self.position = PositionState()

        floating = 0.0
        if self.position.side != 0:
            floating = (next_price - self.position.entry_price) * self.position.side
        reward += floating
        reward -= abs(min(0.0, reward)) * 0.2
        reward -= max(0, self.trade_count - 8) * 0.05
        self.last_equity = reward

        self.step_idx += 1
        terminated = self.step_idx >= len(self.df) - 2
        return self._obs(), reward, terminated, False, {}
