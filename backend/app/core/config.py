from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "VisionGuard"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    database_url: str = "sqlite:///./visionguard.db"
    storage_dir: Path = Path("storage")
    max_upload_mb: int = 100
    video_reconnect_attempts: int = 3
    video_reconnect_backoff_seconds: float = 1.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()