from dataclasses import dataclass


@dataclass
class StrategyContext:
    close: float
    ema_short: float
    ema_long: float
    rsi: float
    volatility: float
    imbalance: float
    unrealized_pnl: float
    distance_to_liq: float
    time_in_trade: float
    direction: int
