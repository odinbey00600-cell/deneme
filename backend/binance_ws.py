from __future__ import annotations

import asyncio
import json
import time

import websockets

from .config import settings
from .market_state import MarketState


class BinanceStream:
    def __init__(self, market: MarketState):
        self.market = market
        sym = settings.symbol.lower()
        self.url = f"wss://fstream.binance.com/stream?streams={sym}@kline_1m/{sym}@markPrice/{sym}@depth5@100ms/{sym}@fundingRate"
        self.running = False

    async def run(self):
        self.running = True
        while self.running:
            try:
                async with websockets.connect(self.url, ping_interval=20, ping_timeout=20) as ws:
                    async for raw in ws:
                        recv_ts = time.time()
                        msg = json.loads(raw)
                        data = msg.get("data", {})
                        et = data.get("e")
                        event_ms = data.get("E", int(recv_ts * 1000))
                        self.market.ws_latency_ms = recv_ts * 1000 - event_ms
                        self.market.heartbeat_ts = recv_ts

                        if et == "kline":
                            k = data["k"]
                            close = float(k["c"])
                            self.market.close_price = close
                            self.market.indicators.update(close)
                            if k.get("x"):
                                self.market.last_kline_close_ts = int(k["T"])
                        elif et == "markPriceUpdate":
                            self.market.mark_price = float(data.get("p", 0))
                        elif et == "depthUpdate":
                            bids = data.get("b", [])
                            asks = data.get("a", [])
                            if bids:
                                self.market.best_bid = float(bids[0][0])
                            if asks:
                                self.market.best_ask = float(asks[0][0])
                        elif et == "fundingRateUpdate":
                            self.market.funding_rate = float(data.get("r", 0))
            except Exception:
                await asyncio.sleep(2)

    async def heartbeat_ok(self) -> bool:
        return time.time() - self.market.heartbeat_ts < 5
