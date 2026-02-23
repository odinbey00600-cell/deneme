def maintenance_margin(notional: float, mmr: float) -> float:
    return abs(notional) * mmr
