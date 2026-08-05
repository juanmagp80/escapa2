"""TravelProfile ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TravelProfile(Base):
    __tablename__ = "travel_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    origin_city: Mapped[str] = mapped_column(String(120))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    default_budget_eur: Mapped[float | None]
    max_drive_minutes: Mapped[int | None]
    preferred_transport: Mapped[str] = mapped_column(String(20), default="EITHER")
    interests: Mapped[list[str]] = mapped_column(JSON, default=list)
    avoid_preferences: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
