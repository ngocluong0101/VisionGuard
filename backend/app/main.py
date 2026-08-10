from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.app.core.config import get_settings
from backend.app.core.logging import configure_logging
from backend.app.db.session import SessionLocal
from backend.app.video.manager import VideoSourceManager


settings = get_settings()
configure_logging(settings.log_level)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.video_source_manager = VideoSourceManager(
        session_factory=SessionLocal,
        reconnect_attempts=settings.video_reconnect_attempts,
        reconnect_backoff_seconds=settings.video_reconnect_backoff_seconds,
        storage_dir=settings.storage_dir,
    )
    try:
        yield
    finally:
        app.state.video_source_manager.stop_all()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "app": settings.app_name,
        "status": "ok",
        "message": "VisionGuard backend foundation is running.",
    }