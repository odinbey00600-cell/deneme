import numpy as np


def encode(ctx) -> np.ndarray:
    return np.array([
        ctx.close, ctx.ema_short, ctx.ema_long, ctx.rsi, ctx.volatility,
        ctx.imbalance, ctx.unrealized_pnl, ctx.distance_to_liq, ctx.time_in_trade, ctx.direction
    ], dtype=np.float32)
