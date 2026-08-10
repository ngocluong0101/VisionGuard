from datetime import datetime

from pydantic import Field, field_validator

from backend.app.models.enums import ZoneType
from backend.app.schemas.base import SchemaBaseModel


class ZoneBase(SchemaBaseModel):
    camera_id: int | None = None
    name: str = Field(min_length=1, max_length=255)
    zone_type: ZoneType
    coordinates: list[list[float]] = Field(default_factory=list)
    enabled: bool = True

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, value: list[list[float]]) -> list[list[float]]:
        if not value:
            raise ValueError("coordinates must contain at least one point")
        for point in value:
            if len(point) != 2:
                raise ValueError("each coordinate point must contain two normalized values")
            if not all(0.0 <= coordinate <= 1.0 for coordinate in point):
                raise ValueError("coordinate values must be normalized between 0 and 1")
        return value


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(SchemaBaseModel):
    camera_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    zone_type: ZoneType | None = None
    coordinates: list[list[float]] | None = None
    enabled: bool | None = None

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, value: list[list[float]] | None) -> list[list[float]] | None:
        if value is None:
            return value
        if not value:
            raise ValueError("coordinates must contain at least one point")
        for point in value:
            if len(point) != 2:
                raise ValueError("each coordinate point must contain two normalized values")
            if not all(0.0 <= coordinate <= 1.0 for coordinate in point):
                raise ValueError("coordinate values must be normalized between 0 and 1")
        return value


class ZoneRead(ZoneBase):
    id: int
    created_at: datetime
    updated_at: datetime