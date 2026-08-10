from collections.abc import Generator

from sqlalchemy.orm import Session

from backend.app.db.session import get_session


def get_db() -> Generator[Session, None, None]:
    yield from get_session()