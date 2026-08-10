from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.base import TimestampMixin
from backend.app.models.enums import ZoneType

if TYPE_CHECKING:
    from backend.app.models.camera import Camera


class Zone(TimestampMixin, Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    camera_id: Mapped[int | None] = mapped_column(ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    zone_type: Mapped[ZoneType] = mapped_column(nullable=False)
    coordinates: Mapped[list[list[float]]] = mapped_column(JSON, nullable=False, default=list)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    camera: Mapped["Camera | None"] = relationship(back_populates="zones")