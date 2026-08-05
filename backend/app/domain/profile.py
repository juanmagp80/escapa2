"""Normalized domain models for the couple travel profile."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import TransportMode


class AirportPreference(BaseModel):
    """An accepted departure airport with its ground transfer data."""

    id: uuid.UUID
    travel_profile_id: uuid.UUID
    iata_code: str = Field(..., min_length=3, max_length=3)
    enabled: bool = True
    transfer_cost_eur: float | None = Field(default=None, ge=0)
    transfer_minutes: int | None = Field(default=None, ge=0)


class TravelProfile(BaseModel):
    """Couple preferences used to find getaways."""

    id: uuid.UUID
    origin_city: str = Field(..., min_length=1, max_length=120)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    default_budget_eur: float | None = Field(default=None, ge=0)
    max_drive_minutes: int | None = Field(default=None, ge=0)
    preferred_transport: TransportMode = TransportMode.EITHER
    interests: list[str] = Field(default_factory=list, max_length=30)
    avoid_preferences: list[str] = Field(default_factory=list, max_length=30)
    created_at: datetime
    updated_at: datetime
