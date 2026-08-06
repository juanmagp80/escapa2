"""Normalized domain models for flight and hotel offers.

These models are provider-agnostic: external providers (e.g. Amadeus) must be
mapped into them before reaching services or routers. Prices always carry an
explicit verification timestamp and an expiry so the UI can warn about stale
or expired quotes.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FlightSearchRequest(BaseModel):
    """A round-trip flight search for two travelers between two airports."""

    origin: str = Field(..., min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$")
    destination: str = Field(..., min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$")
    departure_date: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{4}-\d{2}-\d{2}$")
    return_date: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{4}-\d{2}-\d{2}$")
    travelers: int = Field(default=2, ge=1, le=9)
    currency: str = Field(default="EUR", min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$")


class HotelSearchRequest(BaseModel):
    """A hotel search for a city during a date range."""

    city_code: str = Field(..., min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$")
    check_in_date: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{4}-\d{2}-\d{2}$")
    check_out_date: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{4}-\d{2}-\d{2}$")
    travelers: int = Field(default=2, ge=1, le=9)
    rooms: int = Field(default=1, ge=1, le=4)
    currency: str = Field(default="EUR", min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$")


class FlightOffer(BaseModel):
    """A normalized round-trip flight offer."""

    provider: str = "amadeus"
    provider_offer_id: str = Field(..., max_length=120)
    origin: str = Field(..., min_length=3, max_length=3)
    destination: str = Field(..., min_length=3, max_length=3)
    departure_at: datetime
    arrival_at: datetime
    return_departure_at: datetime
    return_arrival_at: datetime
    base_price_eur: float = Field(..., ge=0)
    baggage_price_eur: float = 0.0
    seat_price_eur: float = 0.0
    total_price_eur: float = Field(..., ge=0)
    travelers: int = Field(default=2, ge=1)
    booking_url: str | None = Field(default=None, max_length=500)
    verified_at: datetime
    expires_at: datetime | None = None


class HotelOffer(BaseModel):
    """A normalized hotel offer for a stay."""

    provider: str = "amadeus"
    provider_offer_id: str = Field(..., max_length=120)
    hotel_name: str = Field(..., max_length=200)
    city_code: str = Field(..., min_length=3, max_length=3)
    check_in: str
    check_out: str
    room_name: str | None = Field(default=None, max_length=200)
    total_price_eur: float = Field(..., ge=0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    taxes_included: bool = False
    free_cancellation_until: datetime | None = None
    breakfast_included: bool = False
    parking_available: bool = False
    rating: float | None = Field(default=None, ge=0, le=5)
    review_count: int | None = Field(default=None, ge=0)
    booking_url: str | None = Field(default=None, max_length=500)
    verified_at: datetime


class RouteRequest(BaseModel):
    """A route cost calculation between two locations."""

    origin: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=200)
    vehicle_id: uuid.UUID | None = None


class RouteOffer(BaseModel):
    """A normalized car-route offer with its cost breakdown."""

    provider: str = "mock"
    provider_offer_id: str = Field(..., max_length=120)
    origin: str
    destination: str
    distance_km: float = Field(..., ge=0)
    duration_minutes: float = Field(..., ge=0)
    fuel_cost_eur: float = Field(default=0.0, ge=0)
    toll_cost_eur: float = Field(default=0.0, ge=0)
    parking_cost_eur: float = Field(default=0.0, ge=0)
    vehicle_wear_cost_eur: float = Field(default=0.0, ge=0)
    total_cost_eur: float = Field(..., ge=0)
    route_polyline: str | None = Field(default=None, max_length=500)
    verified_at: datetime

    @property
    def summed_components(self) -> float:
        """Sum of the explicit components; the total must match this (no tax)."""
        return (
            self.fuel_cost_eur
            + self.toll_cost_eur
            + self.parking_cost_eur
            + self.vehicle_wear_cost_eur
        )


class FuelStationsRequest(BaseModel):
    """Locate fuel stations near a route."""

    origin: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=200)
    vehicle_id: uuid.UUID | None = None


class FuelStation(BaseModel):
    """A fuel station price from the official Spanish service."""

    provider: str = "official"
    station_id: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., max_length=200)
    brand: str | None = Field(default=None, max_length=120)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    price_per_liter_eur: float = Field(..., ge=0)
    fuels_available: list[str] = Field(default_factory=list, max_length=20)
    last_updated: datetime


__all__ = [
    "FlightOffer",
    "FlightSearchRequest",
    "FuelStation",
    "FuelStationsRequest",
    "HotelOffer",
    "HotelSearchRequest",
    "RouteOffer",
    "RouteRequest",
]
