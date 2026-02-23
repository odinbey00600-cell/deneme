import random


def apply_slippage(price: float, side: str, volatility: float) -> float:
    base = random.gauss(0, max(1e-5, volatility) * 0.2)
    signed = abs(base) if side == 'BUY' else -abs(base)
    return price * (1 + signed)
