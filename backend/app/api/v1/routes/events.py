from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.models.event import Event
from backend.app.schemas.event import EventCreate, EventUpdate
from backend.app.services.crud import create_entity, delete_entity, get_entity, list_entities, update_entity

router = APIRouter(prefix="/events", tags=["events"])


def serialize_event(event: Event) -> dict[str, Any]:
    return {
        "id": event.id,
        "camera_id": event.camera_id,
        "event_type": event.event_type,
        "severity": event.severity,
        "timestamp": event.timestamp,
        "track_id": event.track_id,
        "object_class": event.object_class,
        "confidence": event.confidence,
        "snapshot_path": event.snapshot_path,
        "video_path": event.video_path,
        "metadata": event.event_metadata,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
    }


@router.get("")
def list_events(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return [serialize_event(event) for event in list_entities(db, Event)]


@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    event = get_entity(db, Event, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return serialize_event(event)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    event = create_entity(db, Event, payload.model_dump())
    return serialize_event(event)


@router.patch("/{event_id}")
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)) -> dict[str, Any]:
    event = get_entity(db, Event, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    updated_event = update_entity(db, event, payload.model_dump(exclude_unset=True))
    return serialize_event(updated_event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)) -> Response:
    event = get_entity(db, Event, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    delete_entity(db, event)
    return Response(status_code=status.HTTP_204_NO_CONTENT)