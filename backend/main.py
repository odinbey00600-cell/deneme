from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .binance_ws import BinanceStream
from .config import settings
from .db import Database
from .market_state import MarketState
from .simulator import Simulator

app = FastAPI(title="BTCUSDT Futures AI Simulator")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

market = MarketState()
db = Database(str(settings.db_path))
sim = Simulator(db, market)
stream = BinanceStream(market)


@app.on_event("startup")
async def startup():
    await db.connect()
    asyncio.create_task(stream.run())
    asyncio.create_task(sim.run())


@app.get("/api/state")
async def state():
    hb = await stream.heartbeat_ok()
    return {"sim": sim.snapshot(), "ws_connected": hb}


@app.get("/api/replay")
async def replay(path: str = "live_stream.jsonl"):
    file_path = settings.replay_dir / path
    return {"events": sim.replay(Path(file_path))}


@app.websocket("/ws/live")
async def live_socket(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            payload = {"sim": sim.snapshot(), "ws_connected": await stream.heartbeat_ok()}
            await ws.send_json(payload)
            await asyncio.sleep(1)
    except Exception:
        await ws.close()
