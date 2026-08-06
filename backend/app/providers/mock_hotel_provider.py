"""In-memory hotel provider with simulated offers for development and tests."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from app.domain.offers import HotelOffer, HotelSearchRequest


def _offer_id(request: HotelSearchRequest, index: int) -> str:
    raw = f"{request.city_code}|{request.check_in_date}|{request.check_out_date}|{index}"
    return hashlib.sha1(raw.encode("utf-8"), usedforsecurity=False).hexdigest()[:32]


class MockHotelProvider:
    """Serves deterministic hotel offers without touching the network."""

    def __init__(self, base_price_eur: float = 48.0) -> None:
        self._base_price_eur = base_price_eur

    def search(self, request: HotelSearchRequest) -> list[HotelOffer]:
        verified = datetime.now(UTC).replace(microsecond=0)
        return [
            HotelOffer(
                provider_offer_id=_offer_id(request, 0),
                hotel_name="Hotel Céntrico (simulado)",
                city_code=request.city_code,
                check_in=request.check_in_date,
                check_out=request.check_out_date,
                room_name="Doble estándar",
                total_price_eur=round(self._base_price_eur, 2),
                taxes_included=True,
                free_cancellation_until=verified + timedelta(days=1),
                breakfast_included=True,
                parking_available=False,
                rating=4.1,
                review_count=214,
                booking_url=None,
                verified_at=verified,
            )
        ]
