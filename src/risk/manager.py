from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd


@dataclass
class RiskDecision:
    approved: bool
    reason: str


class RiskManager:
    def __init__(self, max_daily_loss_pct: float, max_consecutive_losses: int, cooldown_minutes: int) -> None:
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_consecutive_losses = max_consecutive_losses
        self.cooldown_minutes = cooldown_minutes
        self.day_start_equity: float | None = None
        self.consecutive_losses = 0
        self.cooldown_until: datetime | None = None

    def mark_day_start(self, equity: float) -> None:
        if self.day_start_equity is None:
            self.day_start_equity = equity

    def register_trade_result(self, pnl: float) -> None:
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        if self.consecutive_losses >= self.max_consecutive_losses:
            self.cooldown_until = datetime.utcnow() + timedelta(minutes=self.cooldown_minutes)

    def can_trade(self, equity: float) -> RiskDecision:
        if self.day_start_equity is None:
            self.day_start_equity = equity

        if self.cooldown_until and datetime.utcnow() < self.cooldown_until:
            return RiskDecision(False, "cooldown active")

        dd = (self.day_start_equity - equity) / self.day_start_equity
        if dd >= self.max_daily_loss_pct:
            return RiskDecision(False, "daily loss limit reached")
        return RiskDecision(True, "ok")

    @staticmethod
    def calculate_position_size(equity: float, risk_per_trade: float, entry: float, stop: float) -> float:
        risk_usd = equity * risk_per_trade
        stop_distance = abs(entry - stop)
        if stop_distance <= 0:
            return 0.0
        qty = risk_usd / stop_distance
        return float(max(0.0, qty))

    @staticmethod
    def dynamic_leverage(atr_pct: float, min_lev: int, max_lev: int) -> int:
        scaled = max(min_lev, min(max_lev, int(max_lev - atr_pct * 100)))
        return scaled

    @staticmethod
    def correlation_matrix(closes: dict[str, pd.Series]) -> pd.DataFrame:
        frame = pd.DataFrame(closes).dropna()
        returns = frame.pct_change().dropna()
        return returns.corr()

    @staticmethod
    def correlation_risk_scale(corr_matrix: pd.DataFrame, symbol: str, threshold: float = 0.8) -> float:
        if symbol not in corr_matrix:
            return 1.0
        high_corr = corr_matrix[symbol].drop(labels=[symbol], errors="ignore").abs() > threshold
        return 0.5 if high_corr.any() else 1.0
