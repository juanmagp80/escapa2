"""Route provider contract.

The domain never couples to the raw JSON of an external provider: it only
depends on this protocol and the normalized ``RouteOffer`` model.
"""

from __future__ import annotations

from typing import Protocol

from app.domain.offers import RouteOffer, RouteRequest


class RouteProvider(Protocol):
    """Contract for sources that calculate car route costs."""

    def calculate(self, request: RouteRequest) -> RouteOffer:
        """Return a normalized route offer for the request."""
        ...
