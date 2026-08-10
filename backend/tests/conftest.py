from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from backend.app.api.deps import get_db
from backend.app.db.session import create_db_engine
from backend.app.main import app
from backend.app.video.manager import VideoSourceManager

ROOT_DIR = Path(__file__).resolve().parents[2]


@pytest.fixture()
def database_url(tmp_path: Path) -> str:
    return f"sqlite+pysqlite:///{tmp_path / 'visionguard_test.db'}"


@pytest.fixture()
def migrated_database_url(database_url: str) -> str:
    config = Config(str(ROOT_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")
    return database_url


@pytest.fixture()
def session_factory(migrated_database_url: str):
    engine = create_db_engine(migrated_database_url)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    yield factory
    engine.dispose()


@pytest.fixture()
def db_session(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def video_source_manager(session_factory):
    return VideoSourceManager(
        session_factory=session_factory,
        reconnect_attempts=1,
        reconnect_backoff_seconds=0.05,
        storage_dir=ROOT_DIR / "storage",
    )


@pytest.fixture()
def client(db_session, video_source_manager):
    def override_get_db():
        yield db_session

    def override_get_video_source_manager():
        return video_source_manager

    app.dependency_overrides[get_db] = override_get_db
    from backend.app.api.deps import get_video_source_manager

    app.dependency_overrides[get_video_source_manager] = override_get_video_source_manager
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()