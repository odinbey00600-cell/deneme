from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio


def build_ws_router(app_state):
    router = APIRouter()

    @router.websocket('/ws/live')
    async def live_feed(ws: WebSocket):
        await ws.accept()
        try:
            while True:
                await ws.send_json(app_state.public_state())
                await asyncio.sleep(0.5)
        except WebSocketDisconnect:
            return

    return router
