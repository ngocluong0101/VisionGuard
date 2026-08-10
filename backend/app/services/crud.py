from collections.abc import Mapping
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


def list_entities(session: Session, model: type[ModelT]) -> list[ModelT]:
    return list(session.scalars(select(model).order_by(model.id)).all())


def get_entity(session: Session, model: type[ModelT], entity_id: int) -> ModelT | None:
    return session.get(model, entity_id)


def create_entity(session: Session, model: type[ModelT], payload: Mapping[str, Any]) -> ModelT:
    entity = model(**dict(payload))
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return entity


def update_entity(session: Session, entity: ModelT, payload: Mapping[str, Any]) -> ModelT:
    for key, value in payload.items():
        setattr(entity, key, value)
    session.commit()
    session.refresh(entity)
    return entity


def delete_entity(session: Session, entity: ModelT) -> None:
    session.delete(entity)
    session.commit()