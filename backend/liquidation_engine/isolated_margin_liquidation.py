from backend.risk_engine.margin_usage import margin_ratio


def is_liquidated(maint_margin: float, wallet_balance: float, unrealized_pnl: float) -> tuple[bool, float]:
    ratio = margin_ratio(maint_margin, wallet_balance, unrealized_pnl)
    return ratio >= 1.0, ratio
