"""Amadeus hotel provider with normalization into domain models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.offers import HotelOffer, HotelSearchRequest
from app.providers.amadeus_client import AmadeusClient


class AmadeusHotelProvider:
    """Searches hotels through Amadeus Self-Service Hotels.

    The raw Amadeus JSON is mapped into normalized ``HotelOffer`` models here.
    Each offer is built from the first room/price combination returned by the
    API so the domain always has an explicit total price and currency.
    """

    def __init__(self, client: AmadeusClient) -> None:
        self._client = client

    def search(self, request: HotelSearchRequest) -> list[HotelOffer]:
        payload = self._client.get(
            "/v3/shopping/hotel-offers",
            {
                "cityCode": request.city_code,
                "checkInDate": request.check_in_date,
                "checkOutDate": request.check_out_date,
                "adults": request.travelers,
                "roomQuantity": request.rooms,
                "currencyCode": request.currency,
                "bestRateOnly": True,
                "limit": 10,
            },
        ).json()
        data = payload.get("data")
        if not isinstance(data, list):
            return []
        verified = datetime.now(UTC).replace(microsecond=0)
        offers: list[HotelOffer] = []
        for hotel in data:
            if not isinstance(hotel, dict):
                continue
            mapped = self._map_hotel(hotel, request, verified)
            if mapped is not None:
                offers.append(mapped)
        return offers

    def _map_hotel(
        self,
        hotel: dict[str, Any],
        request: HotelSearchRequest,
        verified: datetime,
    ) -> HotelOffer | None:
        offers = hotel.get("offers") or []
        if not offers:
            return None
        offer = offers[0]
        if not isinstance(offer, dict):
            return None
        price = offer.get("price") or {}
        total = _float(price.get("total"))
        currency = str(price.get("currency") or request.currency)
        policies = offer.get("policies") or {}
        cancellations = self._cancellation_deadline(policies)
        booking_url = self._booking_url(offer)
        room = offer.get("room")
        room_name = (
            str((room or {}).get("typeEstimated", {}).get("category"))
            if isinstance(room, dict)
            else None
        )
        return HotelOffer(
            provider_offer_id=str(offer.get("id") or ""),
            hotel_name=str(hotel.get("name") or "Hotel"),
            city_code=request.city_code,
            check_in=str(offer.get("checkInDate") or request.check_in_date),
            check_out=str(offer.get("checkOutDate") or request.check_out_date),
            room_name=room_name,
            total_price_eur=round(total, 2),
            currency=currency,
            taxes_included=bool(offer.get("price", {}).get("taxes")),
            free_cancellation_until=cancellations,
            breakfast_included=False,
            parking_available=False,
            rating=_float(hotel.get("hotel", {}).get("rating"))
            if isinstance(hotel.get("hotel"), dict)
            else None,
            review_count=None,
            booking_url=booking_url,
            verified_at=verified,
        )

    @staticmethod
    def _cancellation_deadline(policies: Any) -> datetime | None:
        if not isinstance(policies, dict):
            return None
        cancellations = policies.get("cancellations")
        if not isinstance(cancellations, list) or not cancellations:
            return None
        first = cancellations[0]
        if not isinstance(first, dict):
            return None
        deadline = first.get("deadline")
        if isinstance(deadline, str):
            parsed = _iso(deadline)
            if parsed is not None:
                return parsed
        return None

    @staticmethod
    def _booking_url(offer: dict[str, Any]) -> str | None:
        for key in ("self", "booking"):
            link = offer.get(key)
            if isinstance(link, dict) and link.get("href"):
                return str(link["href"])
        return None


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _iso(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed
    except ValueError:
        return None
