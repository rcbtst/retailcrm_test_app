from fastapi import FastAPI, APIRouter

from app.routes.clients import router as clients_router
from app.routes.orders import router as orders_router


def setup_routes(app: FastAPI):
    app.include_router(health_router)
    app.include_router(clients_router)
    app.include_router(orders_router)


health_router = APIRouter(prefix="/health", include_in_schema=False)


@health_router.get("")
async def get_health():
    return {"health": "OK"}
