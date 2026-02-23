from dataclasses import dataclass


@dataclass
class StrategyParams:
    ema_short: int = 9
    ema_long: int = 26
    rsi_low: float = 35
    rsi_high: float = 65
    volatility_max: float = 0.02


def baseline_signal(price: float, ema_short: float, ema_long: float, rsi: float, vol: float, in_position: bool) -> str:
    if vol > 0.02:
        return 'HOLD'
    if not in_position:
        if ema_short > ema_long and rsi < 70:
            return 'OPEN_LONG'
        if ema_short < ema_long and rsi > 30:
            return 'OPEN_SHORT'
        return 'HOLD'
    if abs(ema_short - ema_long) / (price + 1e-9) < 0.0005 or rsi > 75 or rsi < 25:
        return 'CLOSE_POSITION'
    return 'HOLD'
