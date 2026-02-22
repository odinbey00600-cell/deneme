from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from binance.um_futures import UMFutures
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class AccountSnapshot:
    equity: float
    available_balance: float


class BinanceFuturesGateway:
    def __init__(self, api_key: str, api_secret: str, use_testnet: bool = False) -> None:
        base_url = "https://testnet.binancefuture.com" if use_testnet else None
        self.client = UMFutures(key=api_key, secret=api_secret, base_url=base_url)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
    def fetch_klines(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        rows = self.client.klines(symbol=symbol, interval=interval, limit=limit)
        frame = pd.DataFrame(
            rows,
            columns=[
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ],
        )
        numeric_cols = ["open", "high", "low", "close", "volume"]
        frame[numeric_cols] = frame[numeric_cols].astype(float)
        frame["open_time"] = pd.to_datetime(frame["open_time"], unit="ms")
        frame["close_time"] = pd.to_datetime(frame["close_time"], unit="ms")
        return frame

    def get_account_snapshot(self) -> AccountSnapshot:
        account = self.client.balance()
        usdt = next(item for item in account if item["asset"] == "USDT")
        return AccountSnapshot(equity=float(usdt["balance"]), available_balance=float(usdt["availableBalance"]))

    def get_open_positions(self) -> list[dict]:
        positions = self.client.position_risk()
        return [p for p in positions if abs(float(p["positionAmt"])) > 0]

    def set_leverage(self, symbol: str, leverage: int) -> None:
        self.client.change_leverage(symbol=symbol, leverage=leverage)

    def place_market_order(self, symbol: str, side: str, quantity: float, reduce_only: bool = False) -> dict:
        return self.client.new_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity,
            reduceOnly="true" if reduce_only else "false",
            timestamp=int(datetime.utcnow().timestamp() * 1000),
        )

    async def keepalive(self) -> None:
        while True:
            logger.debug("gateway keepalive")
            await asyncio.sleep(30)
