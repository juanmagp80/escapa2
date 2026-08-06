"""VehicleProfile ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VehicleProfile(Base):
    __tablename__ = "vehicle_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    travel_profile_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("travel_profiles.id"))
    name: Mapped[str] = mapped_column(String(120))
    fuel_type: Mapped[str] = mapped_column(String(20), default="GASOLINE")
    average_consumption_l_per_100km: Mapped[float | None]
    tank_capacity_l: Mapped[float | None]
    estimated_cost_per_km_eur: Mapped[float | None]
    max_fuel_detour_minutes: Mapped[int] = mapped_column(Integer, default=15)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
