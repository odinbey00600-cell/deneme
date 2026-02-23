from __future__ import annotations

import asyncio
import random
import time

from execution_interface.base import ExecutionInterface, Position
from liquidation_engine.liquidation import liquidation_price


class SimulatedExecutionEngine(ExecutionInterface):
    def __init__(
        self,
        initial_balance: float,
        leverage: float,
        taker_fee: float,
        maintenance_margin_rate: float,
        min_latency_ms: int,
        max_latency_ms: int,
        slippage_bps_mean: float,
        slippage_bps_std: float,
        seed: int,
    ) -> None:
        self._balance = initial_balance
        self._equity = initial_balance
        self._leverage = leverage
        self._taker_fee = taker_fee
        self._mmr = maintenance_margin_rate
        self._rng = random.Random(seed)
        self._latency = (min_latency_ms, max_latency_ms)
        self._slippage = (slippage_bps_mean, slippage_bps_std)
        self._position = Position()
        self._mark = 0.0

    def _sample_slippage(self) -> float:
        mean, std = self._slippage
        return max(0.0, self._rng.gauss(mean, std) / 10000)

    async def place_order(self, side: str, margin: float, mark_price: float) -> dict:
        if self._position.side != 'FLAT' or margin > self._balance:
            return {'status': 'rejected'}
        await asyncio.sleep(self._rng.randint(*self._latency) / 1000)
        slip = self._sample_slippage()
        exec_price = mark_price * (1 + slip if side == 'LONG' else 1 - slip)
        qty = (margin * self._leverage) / exec_price
        fee = qty * exec_price * self._taker_fee
        self._balance -= (margin + fee)
        self._position = Position(side=side, qty=qty, entry_price=exec_price, margin=margin, opened_ts=time.time())
        return {'status': 'filled', 'price': exec_price, 'qty': qty, 'fee': fee, 'slippage': slip}

    async def close_position(self, mark_price: float, reason: str = 'signal') -> dict:
        if self._position.side == 'FLAT':
            return {'status': 'noop'}
        await asyncio.sleep(self._rng.randint(*self._latency) / 1000)
        slip = self._sample_slippage()
        exec_price = mark_price * (1 - slip if self._position.side == 'LONG' else 1 + slip)
        pnl = (exec_price - self._position.entry_price) * self._position.qty
        if self._position.side == 'SHORT':
            pnl *= -1
        fee = exec_price * self._position.qty * self._taker_fee
        released = self._position.margin + pnl - fee
        self._balance += released
        if self._balance < 0:
            self._balance = 0
        closed = self._position
        self._position = Position()
        self._equity = self._balance
        return {'status': 'filled', 'price': exec_price, 'fee': fee, 'pnl': pnl, 'position': closed, 'reason': reason, 'slippage': slip}

    def funding_payment(self, funding_rate: float) -> float:
        if self._position.side == 'FLAT':
            return 0.0
        notional = self._position.qty * self._mark
        payment = notional * funding_rate
        if self._position.side == 'LONG':
            self._balance -= payment
        else:
            self._balance += payment
        return payment

    def update_mark_price(self, mark_price: float) -> None:
        self._mark = mark_price
        if self._position.side == 'FLAT':
            self._equity = self._balance
            return
        upnl = (mark_price - self._position.entry_price) * self._position.qty
        if self._position.side == 'SHORT':
            upnl *= -1
        self._equity = self._balance + self._position.margin + upnl

    def liquidation_check(self) -> tuple[bool, float]:
        if self._position.side == 'FLAT':
            return False, 0.0
        liq = liquidation_price(
            self._position.entry_price,
            self._position.side,
            self._position.margin,
            self._mmr,
            self._position.qty,
        )
        if self._position.side == 'LONG' and self._mark <= liq:
            self._balance = 0
            self._position = Position()
            self._equity = 0
            return True, liq
        if self._position.side == 'SHORT' and self._mark >= liq:
            self._balance = 0
            self._position = Position()
            self._equity = 0
            return True, liq
        return False, liq

    def get_position(self) -> Position:
        return self._position

    def get_balance(self) -> float:
        return self._balance

    def get_equity(self) -> float:
        return self._equity
