from datetime import datetime

from pydantic import Field

from backend.app.models.enums import CameraStatus, SourceType
from backend.app.schemas.base import SchemaBaseModel


class CameraBase(SchemaBaseModel):
    name: str = Field(min_length=1, max_length=255)
    location_id: int | None = None
    source_type: SourceType
    source_uri: str = Field(min_length=1, max_length=2048)
    status: CameraStatus = CameraStatus.UNKNOWN
    description: str | None = Field(default=None, max_length=2000)


class CameraCreate(CameraBase):
    pass


class CameraUpdate(SchemaBaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    location_id: int | None = None
    source_type: SourceType | None = None
    source_uri: str | None = Field(default=None, min_length=1, max_length=2048)
    status: CameraStatus | None = None
    description: str | None = Field(default=None, max_length=2000)


class CameraRead(CameraBase):
    id: int
    created_at: datetime
    updated_at: datetime