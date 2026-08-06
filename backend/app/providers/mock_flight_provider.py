"""In-memory flight provider with simulated offers for development and tests."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from app.domain.offers import FlightOffer, FlightSearchRequest


def _parse(date: str) -> datetime:
    return datetime.fromisoformat(date).astimezone(UTC)


def _offer_id(request: FlightSearchRequest, index: int) -> str:
    raw = f"{request.origin}|{request.destination}|{request.departure_date}|{index}"
    return hashlib.sha1(raw.encode("utf-8"), usedforsecurity=False).hexdigest()[:32]


class MockFlightProvider:
    """Serves deterministic flight offers without touching the network."""

    def __init__(self, base_price_eur: float = 170.0) -> None:
        self._base_price_eur = base_price_eur

    def search(self, request: FlightSearchRequest) -> list[FlightOffer]:
        departure = _parse(request.departure_date).replace(hour=8, minute=10)
        arrival = departure + timedelta(hours=2, minutes=30)
        return_departure = _parse(request.return_date).replace(hour=19, minute=30)
        return_arrival = return_departure + timedelta(hours=2, minutes=30)
        verified = datetime.now(UTC).replace(microsecond=0)
        total = self._base_price_eur * request.travelers
        return [
            FlightOffer(
                provider_offer_id=_offer_id(request, 0),
                origin=request.origin,
                destination=request.destination,
                departure_at=departure,
                arrival_at=arrival,
                return_departure_at=return_departure,
                return_arrival_at=return_arrival,
                base_price_eur=round(self._base_price_eur, 2),
                total_price_eur=round(total, 2),
                travelers=request.travelers,
                booking_url=None,
                verified_at=verified,
                expires_at=verified + timedelta(days=1),
            )
        ]
