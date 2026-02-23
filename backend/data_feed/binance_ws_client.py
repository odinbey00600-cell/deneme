import asyncio
import json
import time
import websockets
from tenacity import retry, wait_exponential, stop_never


class BinanceWSClient:
    def __init__(self, settings, on_event):
        self.settings = settings
        self.on_event = on_event
        self.running = True

    @retry(wait=wait_exponential(min=1, max=30), stop=stop_never)
    async def connect(self):
        stream_url = f"{self.settings.binance_ws_url}?streams={self.settings.binance_streams}"
        async with websockets.connect(stream_url, ping_interval=self.settings.ws_ping_seconds) as ws:
            while self.running:
                raw = await ws.recv()
                recv_ts = time.time()
                data = json.loads(raw)
                await self.on_event(data, recv_ts)

    async def run(self):
        while self.running:
            try:
                await self.connect()
            except Exception:
                await asyncio.sleep(1)

    def stop(self):
        self.running = False
