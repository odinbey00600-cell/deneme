def taker_fee(notional: float, fee_rate: float) -> float:
    return abs(notional) * fee_rate
