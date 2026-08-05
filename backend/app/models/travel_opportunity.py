"""TravelOpportunity ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TravelOpportunity(Base):
    __tablename__ = "travel_opportunities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    search_watch_id: Mapped[uuid.UUID | None]
    destination_code: Mapped[str] = mapped_column(String(10))
    destination_name: Mapped[str] = mapped_column(String(120))
    transport_mode: Mapped[str] = mapped_column(String(20))
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    useful_hours: Mapped[float | None] = mapped_column(Float)
    total_cost_eur: Mapped[float | None] = mapped_column(Float)
    cost_per_person_eur: Mapped[float | None] = mapped_column(Float)
    cost_per_night_eur: Mapped[float | None] = mapped_column(Float)
    cost_per_useful_hour_eur: Mapped[float | None] = mapped_column(Float)
    comfort_score: Mapped[float | None] = mapped_column(Float)
    value_score: Mapped[float | None] = mapped_column(Float)
    provider_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
