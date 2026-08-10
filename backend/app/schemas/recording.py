from datetime import datetime

from pydantic import Field

from backend.app.schemas.base import SchemaBaseModel


class RecordingBase(SchemaBaseModel):
    camera_id: int | None = None
    event_id: int | None = None
    file_path: str = Field(min_length=1, max_length=2048)
    start_time: datetime
    end_time: datetime


class RecordingCreate(RecordingBase):
    pass


class RecordingUpdate(SchemaBaseModel):
    camera_id: int | None = None
    event_id: int | None = None
    file_path: str | None = Field(default=None, min_length=1, max_length=2048)
    start_time: datetime | None = None
    end_time: datetime | None = None


class RecordingRead(RecordingBase):
    id: int
    created_at: datetime
    updated_at: datetime