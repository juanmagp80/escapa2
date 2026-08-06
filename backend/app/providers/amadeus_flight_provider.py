"""Amadeus flight provider with normalization into domain models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.offers import FlightOffer, FlightSearchRequest
from app.providers.amadeus_client import AmadeusClient


class AmadeusFlightProvider:
    """Searches round-trip flights through Amadeus Self-Service.

    The raw Amadeus JSON is mapped into normalized ``FlightOffer`` models here,
    so the rest of the system never depends on the provider schema. Prices are
    the total for the requested number of travelers.
    """

    def __init__(self, client: AmadeusClient) -> None:
        self._client = client

    def search(self, request: FlightSearchRequest) -> list[FlightOffer]:
        payload = self._client.get(
            "/v2/shopping/flight-offers",
            {
                "originLocationCode": request.origin,
                "destinationLocationCode": request.destination,
                "departureDate": request.departure_date,
                "returnDate": request.return_date,
                "adults": request.travelers,
                "currencyCode": request.currency,
                "max": 10,
            },
        ).json()
        data = payload.get("data")
        if not isinstance(data, list):
            return []
        verified = datetime.now(UTC).replace(microsecond=0)
        return [self._map_offer(item, verified) for item in data if isinstance(item, dict)]

    def _map_offer(self, item: dict[str, Any], verified: datetime) -> FlightOffer:
        itineraries = item.get("itineraries") or []
        outbound = self._first_flight(itineraries, 0)
        inbound = self._first_flight(itineraries, 1)
        price = item.get("price") or {}
        fees = price.get("fees") or []
        base = _float(price.get("base"))
        total = _float(price.get("grandTotal"))
        baggage_total = sum(_float(fee.get("amount")) for fee in fees if isinstance(fee, dict))
        booking_links = item.get("travelerPricings") or []
        booking_url = self._booking_url(booking_links)
        return FlightOffer(
            provider_offer_id=str(item.get("id") or ""),
            origin=str(outbound.get("iataCode") or ""),
            destination=str((outbound.get("arrival") or {}).get("iataCode") or ""),
            departure_at=_iso(outbound.get("departure", {}).get("at")),
            arrival_at=_iso(outbound.get("arrival", {}).get("at")),
            return_departure_at=_iso(inbound.get("departure", {}).get("at")),
            return_arrival_at=_iso(inbound.get("arrival", {}).get("at")),
            base_price_eur=round(base, 2),
            baggage_price_eur=round(baggage_total, 2),
            seat_price_eur=0.0,
            total_price_eur=round(total, 2),
            booking_url=booking_url,
            verified_at=verified,
            expires_at=None,
        )

    @staticmethod
    def _first_flight(itineraries: list[Any], index: int) -> dict[str, Any]:
        if index >= len(itineraries):
            return {}
        itinerary = itineraries[index]
        segments = itinerary.get("segments") if isinstance(itinerary, dict) else None
        if isinstance(segments, list) and segments:
            return segments[0] if isinstance(segments[0], dict) else {}
        return {}

    @staticmethod
    def _booking_url(traveler_pricings: list[Any]) -> str | None:
        for pricing in traveler_pricings:
            if not isinstance(pricing, dict):
                continue
            fare_details = pricing.get("fareDetailsBySegment") or []
            for detail in fare_details:
                if not isinstance(detail, dict):
                    continue
                branded = detail.get("brandedFare")
                if isinstance(branded, dict):
                    return branded.get("detailUrl")
        return None


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _iso(value: Any) -> datetime:
    if not isinstance(value, str):
        return datetime.now(UTC).replace(microsecond=0)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed
    except ValueError:
        return datetime.now(UTC).replace(microsecond=0)
