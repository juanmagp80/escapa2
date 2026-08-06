"""Normalized domain models for travel opportunities.

These models are provider-agnostic: external providers must be mapped into
them before reaching services or routers.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import TransportMode


class Opportunity(BaseModel):
    """A complete trip suggestion with metrics and verification metadata.

    Origin, interests, the cost breakdown and the booking URL are optional
    informational fields. They are populated by providers that can supply them
    and are never invented by the AI layer.
    """

    id: uuid.UUID
    destination_code: str = Field(..., max_length=10)
    destination_name: str = Field(..., max_length=120)
    transport_mode: TransportMode
    start_at: datetime
    end_at: datetime
    useful_hours: float | None = None
    total_cost_eur: float | None = None
    cost_per_person_eur: float | None = None
    cost_per_night_eur: float | None = None
    cost_per_useful_hour_eur: float | None = None
    comfort_score: float | None = None
    value_score: float | None = None
    provider_verified_at: datetime | None = None
    origin_city: str | None = Field(default=None, max_length=120)
    interests: list[str] = Field(default_factory=list, max_length=30)
    flight_cost_eur: float | None = None
    hotel_cost_eur: float | None = None
    route_cost_eur: float | None = None
    booking_url: str | None = Field(default=None, max_length=500)


class PriceSnapshot(BaseModel):
    """A price point captured at a given time for an opportunity."""

    id: uuid.UUID
    travel_opportunity_id: uuid.UUID
    total_cost_eur: float | None = None
    flight_cost_eur: float | None = None
    hotel_cost_eur: float | None = None
    route_cost_eur: float | None = None
    local_transport_cost_eur: float | None = None
    fees_cost_eur: float | None = None
    captured_at: datetime
    source_summary_json: dict[str, object] = Field(default_factory=dict)
