from backend.app.core.config import get_settings


def test_settings_reads_database_url_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///./test_settings.db")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.database_url == "sqlite+pysqlite:///./test_settings.db"

    get_settings.cache_clear()