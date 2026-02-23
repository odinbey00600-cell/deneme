from __future__ import annotations

from collections import deque
from math import sqrt


class IndicatorState:
    def __init__(self, rsi_period: int = 14, vol_window: int = 20):
        self.prices: deque[float] = deque(maxlen=300)
        self.rsi_period = rsi_period
        self.vol_window = vol_window

    def update(self, close: float) -> None:
        self.prices.append(close)

    def ema(self, period: int) -> float:
        if not self.prices:
            return 0.0
        alpha = 2 / (period + 1)
        value = self.prices[0]
        for p in list(self.prices)[1:]:
            value = alpha * p + (1 - alpha) * value
        return value

    def rsi(self) -> float:
        if len(self.prices) < self.rsi_period + 1:
            return 50.0
        gains, losses = 0.0, 0.0
        data = list(self.prices)[-(self.rsi_period + 1) :]
        for i in range(1, len(data)):
            delta = data[i] - data[i - 1]
            if delta >= 0:
                gains += delta
            else:
                losses -= delta
        if losses == 0:
            return 100.0
        rs = gains / losses
        return 100 - (100 / (1 + rs))

    def volatility(self) -> float:
        if len(self.prices) < self.vol_window:
            return 0.0
        values = list(self.prices)[-self.vol_window :]
        mean = sum(values) / len(values)
        var = sum((v - mean) ** 2 for v in values) / len(values)
        return sqrt(var) / mean if mean else 0.0
