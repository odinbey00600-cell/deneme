from __future__ import annotations

from dataclasses import dataclass

from loguru import logger

from src.data.binance_client import BinanceFuturesGateway


@dataclass
class PlannedOrder:
    symbol: str
    direction: int
    qty: float
    leverage: int
    stop_loss: float
    take_profit: float


class OrderExecutor:
    def __init__(self, gateway: BinanceFuturesGateway) -> None:
        self.gateway = gateway

    def execute(self, order: PlannedOrder) -> dict:
        side = "BUY" if order.direction > 0 else "SELL"
        self.gateway.set_leverage(order.symbol, order.leverage)
        response = self.gateway.place_market_order(order.symbol, side, round(order.qty, 3))
        logger.info(
            "ORDER symbol={} side={} qty={} lev={} sl={} tp={}",
            order.symbol,
            side,
            order.qty,
            order.leverage,
            order.stop_loss,
            order.take_profit,
        )
        return response
