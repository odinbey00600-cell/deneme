from fastapi import APIRouter


def build_metrics_router(app_state):
    router = APIRouter()

    @router.get('/metrics')
    async def metrics():
        s = app_state.public_state()
        return {
            'generation_id': s['generation_id'],
            'balance': s['balance'],
            'equity': s['equity'],
            'latency_ms': s['latency_ms'],
            'ws_healthy': s['ws_healthy'],
            'liquidations': s['liquidations']
        }

    return router
