from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from backend.app.models.enums import EventType, SeverityLevel
from backend.app.schemas.base import SchemaBaseModel


class EventBase(SchemaBaseModel):
    camera_id: int | None = None
    event_type: EventType
    severity: SeverityLevel = SeverityLevel.INFO
    timestamp: datetime
    track_id: int | None = None
    object_class: str | None = Field(default=None, max_length=255)
    confidence: float | None = None
    snapshot_path: str | None = Field(default=None, max_length=2048)
    video_path: str | None = Field(default=None, max_length=2048)
    event_metadata: dict[str, Any] = Field(default_factory=dict, alias="metadata")

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        return value


class EventCreate(EventBase):
    pass


class EventUpdate(SchemaBaseModel):
    camera_id: int | None = None
    event_type: EventType | None = None
    severity: SeverityLevel | None = None
    timestamp: datetime | None = None
    track_id: int | None = None
    object_class: str | None = Field(default=None, max_length=255)
    confidence: float | None = None
    snapshot_path: str | None = Field(default=None, max_length=2048)
    video_path: str | None = Field(default=None, max_length=2048)
    event_metadata: dict[str, Any] | None = Field(default=None, alias="metadata")

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        return value


class EventRead(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime