def calculate_imbalance(bids: list[list[float]], asks: list[list[float]]) -> float:
    bid_vol = sum(float(q) for _, q in bids)
    ask_vol = sum(float(q) for _, q in asks)
    denom = bid_vol + ask_vol
    return 0.0 if denom == 0 else (bid_vol - ask_vol) / denom
