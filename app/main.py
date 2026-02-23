from __future__ import annotations

import asyncio
from pathlib import Path

from app.bot.manager import BotManager
from app.config import settings

manager = BotManager()

if not settings.sandbox_mode:
    from fastapi import FastAPI
    from fastapi.responses import FileResponse

    app = FastAPI(title="Institutional Paper Trading Lab", version="1.0.0")

    @app.on_event("startup")
    async def startup() -> None:
        asyncio.create_task(manager.run())

    @app.get("/api/state")
    async def state() -> dict:
        return manager.current_state()

    @app.post("/api/pause")
    async def pause() -> dict:
        manager.pause()
        return {"ok": True}

    @app.post("/api/resume")
    async def resume() -> dict:
        manager.resume()
        return {"ok": True}

    @app.post("/api/kill")
    async def kill() -> dict:
        manager.kill_bot()
        return {"ok": True}

    @app.post("/api/reset-learning")
    async def reset_learning() -> dict:
        manager.reset_learning()
        return {"ok": True}

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(Path("app/ui/index.html"))
else:
    app = None
