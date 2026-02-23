from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime

import websockets

from config_manager.settings import settings
from market_state_engine.state import Candle, MarketState


class BinanceDataFeed:
    def __init__(self, market_state: MarketState):
        self.market_state = market_state
        self.last_seq = None
        self.last_heartbeat = time.time()
        self.stream_url = (
            f"{settings.ws_base}{settings.ws_symbol}@kline_1m/"
            f"{settings.ws_symbol}@markPrice/"
            f"{settings.ws_symbol}@depth5@100ms/"
            f"{settings.ws_symbol}@fundingRate"
        )

    async def run(self) -> None:
        while True:
            try:
                async with websockets.connect(self.stream_url, ping_interval=10) as ws:
                    self.market_state.ws_healthy = True
                    async for raw in ws:
                        started = time.time()
                        data = json.loads(raw)
                        self.last_heartbeat = time.time()
                        await self._handle_message(data)
                        self.market_state.last_update_latency_ms = (time.time() - started) * 1000
            except Exception:
                self.market_state.ws_healthy = False
                await asyncio.sleep(1)

    async def _handle_message(self, payload: dict) -> None:
        stream = payload.get('stream', '')
        data = payload.get('data', {})
        if 'kline' in stream:
            k = data.get('k', {})
            self.market_state.candles.append(
                Candle(
                    ts=datetime.fromtimestamp(k['t'] / 1000),
                    open=float(k['o']),
                    high=float(k['h']),
                    low=float(k['l']),
                    close=float(k['c']),
                    volume=float(k['v']),
                    closed=bool(k['x']),
                )
            )
        elif 'markPrice' in stream:
            self.market_state.mark_price = float(data.get('p', 0.0))
        elif 'depth5' in stream:
            bids = data.get('b', [])
            asks = data.get('a', [])
            bid_vol = sum(float(b[1]) for b in bids)
            ask_vol = sum(float(a[1]) for a in asks)
            denom = (bid_vol + ask_vol) + 1e-9
            self.market_state.order_book_imbalance = (bid_vol - ask_vol) / denom
            seq = data.get('u')
            if self.last_seq and seq and seq <= self.last_seq:
                self.market_state.missing_data_events += 1
            if seq:
                self.last_seq = seq
        elif 'fundingRate' in stream:
            self.market_state.funding_rate = float(data.get('r', 0.0))

    def heartbeat_ok(self) -> bool:
        return time.time() - self.last_heartbeat <= settings.heartbeat_timeout_seconds
