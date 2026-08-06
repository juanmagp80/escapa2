"""Fuel-price provider contract.

The domain never couples to the raw JSON of the official service: it only
depends on this protocol and the normalized ``FuelStation`` model.
"""

from __future__ import annotations

from typing import Protocol

from app.domain.offers import FuelStation, FuelStationsRequest


class FuelPriceProvider(Protocol):
    """Contract for sources that locate fuel stations near a route."""

    def stations_near_route(self, request: FuelStationsRequest) -> list[FuelStation]:
        """Return the fuel stations whose price is worth a detour."""
        ...
