from datetime import datetime

from pydantic import Field

from backend.app.schemas.base import SchemaBaseModel


class LocationBase(SchemaBaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class LocationCreate(LocationBase):
    pass


class LocationUpdate(SchemaBaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class LocationRead(LocationBase):
    id: int
    created_at: datetime
    updated_at: datetime