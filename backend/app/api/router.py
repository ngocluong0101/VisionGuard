from fastapi import APIRouter

from backend.app.api.routes.health import router as health_router
from backend.app.api.v1.router import api_v1_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(api_v1_router)