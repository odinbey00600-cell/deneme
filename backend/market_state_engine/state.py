from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque


@dataclass
class Candle:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    closed: bool


@dataclass
class MarketState:
    candles: Deque[Candle] = field(default_factory=lambda: deque(maxlen=5000))
    mark_price: float = 0.0
    funding_rate: float = 0.0
    order_book_imbalance: float = 0.0
    last_update_latency_ms: float = 0.0
    ws_healthy: bool = True
    missing_data_events: int = 0

    def latest_close(self) -> float:
        return self.candles[-1].close if self.candles else 0.0
