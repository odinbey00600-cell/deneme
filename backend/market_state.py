from __future__ import annotations

from dataclasses import dataclass, field
from time import time

from .indicators import IndicatorState


@dataclass
class MarketState:
    mark_price: float = 0.0
    close_price: float = 0.0
    best_bid: float = 0.0
    best_ask: float = 0.0
    funding_rate: float = 0.0
    ws_latency_ms: float = 0.0
    last_kline_close_ts: int = 0
    heartbeat_ts: float = field(default_factory=time)
    indicators: IndicatorState = field(default_factory=IndicatorState)

    def order_book_imbalance(self) -> float:
        denom = self.best_bid + self.best_ask
        if denom == 0:
            return 0.0
        return (self.best_bid - self.best_ask) / denom
