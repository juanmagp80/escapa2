"""AirportPreference ORM model."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AirportPreference(Base):
    __tablename__ = "airport_preferences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    travel_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("travel_profiles.id"), index=True
    )
    iata_code: Mapped[str] = mapped_column(String(3))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    transfer_cost_eur: Mapped[float | None] = mapped_column(Float)
    transfer_minutes: Mapped[int | None] = mapped_column(Integer)
