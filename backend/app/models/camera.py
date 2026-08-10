from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.base import TimestampMixin
from backend.app.models.enums import CameraStatus, SourceType

if TYPE_CHECKING:
    from backend.app.models.event import Event
    from backend.app.models.location import Location
    from backend.app.models.recording import Recording
    from backend.app.models.zone import Zone


class Camera(TimestampMixin, Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    source_type: Mapped[SourceType] = mapped_column(nullable=False)
    source_uri: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default=CameraStatus.UNKNOWN.value)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    location: Mapped["Location | None"] = relationship(back_populates="cameras")
    zones: Mapped[list["Zone"]] = relationship(back_populates="camera")
    events: Mapped[list["Event"]] = relationship(back_populates="camera")
    recordings: Mapped[list["Recording"]] = relationship(back_populates="camera")