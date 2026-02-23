import asyncio
from backend.data_feed.binance_ws_client import BinanceWSClient


class StreamManager:
    def __init__(self, settings, on_event):
        self.client = BinanceWSClient(settings, on_event)
        self.task = None

    async def start(self):
        self.task = asyncio.create_task(self.client.run())

    async def stop(self):
        self.client.stop()
        if self.task:
            await self.task
