"""PriceSnapshot ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    travel_opportunity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("travel_opportunities.id"), index=True
    )
    total_cost_eur: Mapped[float | None] = mapped_column(Float)
    flight_cost_eur: Mapped[float | None] = mapped_column(Float)
    hotel_cost_eur: Mapped[float | None] = mapped_column(Float)
    route_cost_eur: Mapped[float | None] = mapped_column(Float)
    local_transport_cost_eur: Mapped[float | None] = mapped_column(Float)
    fees_cost_eur: Mapped[float | None] = mapped_column(Float)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    source_summary_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
