"""Hotel provider contract.

The domain never couples to the raw JSON of an external provider: it only
depends on this protocol and the normalized ``HotelOffer`` model.
"""

from __future__ import annotations

from typing import Protocol

from app.domain.offers import HotelOffer, HotelSearchRequest


class HotelProvider(Protocol):
    """Contract for sources that search hotels for a stay."""

    def search(self, request: HotelSearchRequest) -> list[HotelOffer]:
        """Return normalized hotel offers for the request."""
        ...
