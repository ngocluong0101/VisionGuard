from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.base import TimestampMixin
from backend.app.models.enums import EventType, SeverityLevel

if TYPE_CHECKING:
    from backend.app.models.camera import Camera
    from backend.app.models.recording import Recording


class Event(TimestampMixin, Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    camera_id: Mapped[int | None] = mapped_column(ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    event_type: Mapped[EventType] = mapped_column(nullable=False)
    severity: Mapped[SeverityLevel] = mapped_column(nullable=False, default=SeverityLevel.INFO)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    track_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    object_class: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    snapshot_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)

    camera: Mapped["Camera | None"] = relationship(back_populates="events")
    recordings: Mapped[list["Recording"]] = relationship(back_populates="event")