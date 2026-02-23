def apply_funding(balance: float, position_notional: float, funding_rate: float) -> float:
    return balance - (position_notional * funding_rate)
