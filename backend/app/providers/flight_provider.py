"""Flight provider contract.

The domain never couples to the raw JSON of an external provider: it only
depends on this protocol and the normalized ``FlightOffer`` model.
"""

from __future__ import annotations

from typing import Protocol

from app.domain.offers import FlightOffer, FlightSearchRequest


class FlightProvider(Protocol):
    """Contract for sources that search round-trip flights."""

    def search(self, request: FlightSearchRequest) -> list[FlightOffer]:
        """Return normalized round-trip flight offers for the request."""
        ...
