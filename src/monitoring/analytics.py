from __future__ import annotations

import numpy as np
import pandas as pd


class PerformanceAnalytics:
    def __init__(self) -> None:
        self.trades: list[dict] = []

    def add_trade(self, trade: dict) -> None:
        self.trades.append(trade)

    def equity_curve(self) -> pd.Series:
        if not self.trades:
            return pd.Series(dtype=float)
        pnl = pd.Series([t["pnl"] for t in self.trades])
        return pnl.cumsum()

    def max_drawdown(self) -> float:
        curve = self.equity_curve()
        if curve.empty:
            return 0.0
        peak = curve.cummax()
        dd = curve - peak
        return float(dd.min())

    def sharpe(self) -> float:
        if len(self.trades) < 2:
            return 0.0
        rets = np.array([t["pnl"] for t in self.trades])
        if rets.std() == 0:
            return 0.0
        return float((rets.mean() / rets.std()) * np.sqrt(252))
