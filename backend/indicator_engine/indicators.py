from __future__ import annotations

import numpy as np


def ema(values: list[float], period: int) -> float:
    if not values:
        return 0.0
    arr = np.array(values[-max(period * 3, period):], dtype=np.float64)
    alpha = 2 / (period + 1)
    ema_val = arr[0]
    for x in arr[1:]:
        ema_val = alpha * x + (1 - alpha) * ema_val
    return float(ema_val)


def rsi(values: list[float], period: int = 14) -> float:
    if len(values) < period + 1:
        return 50.0
    deltas = np.diff(np.array(values[-(period + 1):], dtype=np.float64))
    gains = np.clip(deltas, 0, None)
    losses = -np.clip(deltas, None, 0)
    avg_gain = np.mean(gains) + 1e-12
    avg_loss = np.mean(losses) + 1e-12
    rs = avg_gain / avg_loss
    return float(100 - (100 / (1 + rs)))


def volatility(values: list[float], window: int = 30) -> float:
    if len(values) < window:
        return 0.0
    series = np.array(values[-window:], dtype=np.float64)
    returns = np.diff(series) / (series[:-1] + 1e-12)
    return float(np.std(returns))
