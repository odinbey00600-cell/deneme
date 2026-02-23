from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskDecision:
    approved: bool
    reason: str
    leverage: int
    qty: float


class RiskManager:
    def __init__(self, max_risk_per_trade: float, min_lev: int, max_lev: int) -> None:
        self.max_risk_per_trade = max_risk_per_trade
        self.min_lev = min_lev
        self.max_lev = max_lev

    def dynamic_leverage(self, atr_ratio: float) -> int:
        if atr_ratio > 0.03:
            return self.min_lev
        if atr_ratio > 0.015:
            return max(self.min_lev, self.max_lev // 2)
        return self.max_lev

    def assess(
        self,
        equity: float,
        price: float,
        atr: float,
        daily_loss: float,
        daily_limit: float,
        consecutive_losses: int,
        max_consecutive_losses: int,
    ) -> RiskDecision:
        if daily_loss <= -abs(daily_limit * equity):
            return RiskDecision(False, "daily max loss reached", 1, 0.0)
        if consecutive_losses >= max_consecutive_losses:
            return RiskDecision(False, "cooldown: consecutive losses", 1, 0.0)
        atr_ratio = atr / (price + 1e-9)
        leverage = self.dynamic_leverage(atr_ratio)
        stop_distance = max(atr * 1.5, price * 0.002)
        risk_budget = equity * self.max_risk_per_trade
        qty = max(risk_budget / (stop_distance + 1e-9), 0.0)
        if qty * price / leverage > equity:
            qty = equity * leverage / price
        if qty <= 0:
            return RiskDecision(False, "insufficient margin", leverage, 0.0)
        return RiskDecision(True, "risk approved", leverage, qty)
