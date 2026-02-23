from __future__ import annotations


def liquidation_price(entry: float, side: str, initial_margin: float, maintenance_margin_rate: float, position_size: float) -> float:
    maintenance_margin = position_size * maintenance_margin_rate
    if position_size <= 0:
        return 0.0
    cushion = (initial_margin - maintenance_margin) / position_size
    if side == 'LONG':
        return entry * (1 - cushion)
    return entry * (1 + cushion)
