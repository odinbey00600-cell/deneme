from fastapi import APIRouter


def build_rest_router(app_state):
    router = APIRouter(prefix='/api')

    @router.get('/health')
    async def health():
        return app_state.health_snapshot()

    @router.get('/status')
    async def status():
        return app_state.public_state()

    @router.get('/lineage')
    async def lineage():
        return {'edges': app_state.lineage.as_edges()}

    return router
