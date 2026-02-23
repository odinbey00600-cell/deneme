from __future__ import annotations

import asyncio
import json
import random
from collections import defaultdict, deque

from app.config import settings


class BinanceMarketFeed:
    def __init__(self, symbols: list[str], deterministic: bool = False) -> None:
        self.symbols = symbols
        self.latest: dict[str, float] = {s: 0.0 for s in symbols}
        self.frames: dict[str, deque] = defaultdict(lambda: deque(maxlen=300))
        self.connected = False
        self.deterministic = deterministic
        self._rng = random.Random(42)

    def bootstrap_price(self, symbol: str) -> float:
        base = {"btcusdt": 50000, "ethusdt": 3000, "solusdt": 120, "bnbusdt": 550}
        return float(base.get(symbol, 100.0))

    async def run(self) -> None:
        for s in self.symbols:
            p = self.bootstrap_price(s)
            self.latest[s] = p
            self.frames[s].append({"open": p, "high": p, "low": p, "close": p, "volume": 1.0})

        if settings.sandbox_mode:
            while True:
                await self._simulate_tick()
            
        streams = "/".join([f"{s}@miniTicker" for s in self.symbols])
        url = f"wss://fstream.binance.com/stream?streams={streams}"
        while True:
            try:
                import websockets

                async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
                    self.connected = True
                    while True:
                        msg = await ws.recv()
                        payload = json.loads(msg)["data"]
                        symbol = payload["s"].lower()
                        price = float(payload["c"])
                        self._ingest(symbol, price)
            except Exception:
                self.connected = False
                await self._simulate_tick()

    async def _simulate_tick(self) -> None:
        for symbol in self.symbols:
            prev = self.latest[symbol] or self.bootstrap_price(symbol)
            drift = 0.0002 if symbol in ("btcusdt", "ethusdt") else -0.0001
            shock = self._rng.uniform(-0.001, 0.001) if self.deterministic else random.uniform(-0.001, 0.001)
            nxt = max(prev * (1 + drift + shock), 0.01)
            self._ingest(symbol, nxt)
        await asyncio.sleep(0 if self.deterministic else 1)

    def _ingest(self, symbol: str, price: float) -> None:
        self.latest[symbol] = price
        vol = self._rng.uniform(1, 100) if self.deterministic else random.uniform(1, 100)
        bar = {"open": price, "high": price, "low": price, "close": price, "volume": vol}
        self.frames[symbol].append(bar)

    def frame(self, symbol: str):
        return list(self.frames[symbol])

    async def seed_ticks(self, ticks: int) -> None:
        for _ in range(ticks):
            await self._simulate_tick()
