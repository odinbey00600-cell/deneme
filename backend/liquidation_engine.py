from __future__ import annotations

from .config import settings


class LiquidationEngine:
    @staticmethod
    def liquidation_price(entry: float, qty: float, margin: float, side: int) -> float:
        if qty == 0:
            return 0.0
        maint = margin * settings.maintenance_margin_rate
        if side > 0:
            return entry - (margin - maint) / qty
        return entry + (margin - maint) / abs(qty)

    @staticmethod
    def should_liquidate(mark: float, liq: float, side: int) -> bool:
        if side > 0:
            return mark <= liq
        if side < 0:
            return mark >= liq
        return False
