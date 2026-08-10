from fastapi import APIRouter

from backend.app.api.v1.routes.cameras import router as cameras_router
from backend.app.api.v1.routes.events import router as events_router
from backend.app.api.v1.routes.locations import router as locations_router
from backend.app.api.v1.routes.recordings import router as recordings_router
from backend.app.api.v1.routes.zones import router as zones_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(locations_router)
api_v1_router.include_router(cameras_router)
api_v1_router.include_router(zones_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(recordings_router)