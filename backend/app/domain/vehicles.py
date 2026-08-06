"""Normalized domain model for the couple vehicle profile.

The vehicle defines how fuel costs are estimated on car trips: average
consumption for the route fuel cost, tank capacity for the fuel-station
net-savings calculation and estimated cost per kilometer for vehicle wear.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.domain.enums import FuelType


class VehicleProfile(BaseModel):
    """The default vehicle used to estimate car-trip costs."""

    id: uuid.UUID
    travel_profile_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=120)
    fuel_type: FuelType = FuelType.GASOLINE
    average_consumption_l_per_100km: float | None = Field(default=None, ge=0)
    tank_capacity_l: float | None = Field(default=None, ge=0)
    estimated_cost_per_km_eur: float | None = Field(default=None, ge=0)
    max_fuel_detour_minutes: int = Field(default=15, ge=0)
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def _require_fuel_relevant_fields(self) -> VehicleProfile:
        if self.fuel_type == FuelType.ELECTRIC:
            return self
        if self.average_consumption_l_per_100km is None:
            raise ValueError(
                "average_consumption_l_per_100km is required for non-electric vehicles"
            )
        return self


__all__ = ["VehicleProfile"]
