import asyncio
import random


async def apply_latency(min_ms: int, max_ms: int) -> int:
    delay = random.randint(min_ms, max_ms)
    await asyncio.sleep(delay / 1000)
    return delay
