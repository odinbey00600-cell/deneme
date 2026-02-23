from backend.strategy_engine.strategy_context import StrategyContext


def decide(ctx: StrategyContext) -> str:
    if ctx.direction == 0:
        if ctx.ema_short > ctx.ema_long and ctx.rsi < 70:
            return 'OPEN_LONG'
        if ctx.ema_short < ctx.ema_long and ctx.rsi > 30:
            return 'OPEN_SHORT'
        return 'HOLD'
    if ctx.direction == 1 and (ctx.rsi > 75 or ctx.ema_short < ctx.ema_long):
        return 'CLOSE_POSITION'
    if ctx.direction == -1 and (ctx.rsi < 25 or ctx.ema_short > ctx.ema_long):
        return 'CLOSE_POSITION'
    return 'HOLD'
