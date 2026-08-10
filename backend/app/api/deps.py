from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from backend.app.db.session import get_session
from backend.app.video.manager import VideoSourceManager


def get_db() -> Generator[Session, None, None]:
    yield from get_session()


def get_video_source_manager(request: Request) -> VideoSourceManager:
    return request.app.state.video_source_manager