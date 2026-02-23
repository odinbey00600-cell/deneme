from __future__ import annotations

import asyncio
import random

from .config import settings


class ExecutionEngine:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)

    async def execute_price(self, mark_price: float, side: str) -> tuple[float, float, int]:
        latency = self.rng.randint(settings.min_latency_ms, settings.max_latency_ms)
        await asyncio.sleep(latency / 1000)
        slip = self.rng.uniform(-settings.slippage_bps, settings.slippage_bps) / 10_000
        slipped = mark_price * (1 + slip if side == "BUY" else 1 - slip)
        fee = slipped * settings.taker_fee_rate
        return slipped, fee, latency
