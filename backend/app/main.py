from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.app.core.config import get_settings
from backend.app.core.logging import configure_logging


settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "app": settings.app_name,
        "status": "ok",
        "message": "VisionGuard backend foundation is running.",
    }