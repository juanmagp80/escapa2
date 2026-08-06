"""Tests for the Amadeus provider infrastructure.

Real Amadeus endpoints are never called: httpx.MockTransport simulates the
token endpoint and the data endpoints so the normalization and HTTP handling
are verified offline.
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pytest
from app.core.config import Settings
from app.core.errors import ProviderUnavailableError
from app.domain.offers import (
    FlightSearchRequest,
    HotelSearchRequest,
)
from app.providers.amadeus_client import AmadeusClient
from app.providers.amadeus_flight_provider import AmadeusFlightProvider
from app.providers.amadeus_hotel_provider import AmadeusHotelProvider
from app.providers.factory import build_flight_provider, build_hotel_provider
from app.providers.mock_flight_provider import MockFlightProvider
from app.providers.mock_hotel_provider import MockHotelProvider

_TOKEN_RESPONSE = {
    "type": "amadeusOAuth2Token",
    "username": "test",
    "application_name": "escapa2",
    "client_id": "test",
    "token_type": "Bearer",
    "access_token": "TOKEN-123",
    "expires_in": 1799,
    "state": "approved",
}


def _token_handler(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/oauth2/token"):
        return httpx.Response(200, json=_TOKEN_RESPONSE)
    if request.url.path.endswith("/v2/shopping/flight-offers"):
        return httpx.Response(200, json=_flight_payload())
    if request.url.path.endswith("/v3/shopping/hotel-offers"):
        return httpx.Response(200, json=_hotel_payload())
    return httpx.Response(404)


def _amadeus_settings(**overrides: object) -> Settings:
    base = {
        "APP_ENV": "test",
        "GEMINI_ENABLED": "false",
        "AMADEUS_ENABLED": "true",
        "AMADEUS_CLIENT_ID": "client-id",
        "AMADEUS_CLIENT_SECRET": "client-secret",
    }
    base.update(overrides)
    return Settings(**base)  # type: ignore[arg-type]


def _flight_payload() -> dict[str, object]:
    return {
        "data": [
            {
                "id": "flight-1",
                "itineraries": [
                    {
                        "segments": [
                            {
                                "iataCode": "MAD",
                                "departure": {"at": "2026-09-01T08:10:00+02:00"},
                                "arrival": {
                                    "iataCode": "OPO",
                                    "at": "2026-09-01T09:40:00+02:00",
                                },
                            }
                        ]
                    },
                    {
                        "segments": [
                            {
                                "iataCode": "OPO",
                                "departure": {"at": "2026-09-03T19:30:00+02:00"},
                                "arrival": {
                                    "iataCode": "MAD",
                                    "at": "2026-09-03T21:00:00+02:00",
                                },
                            }
                        ]
                    },
                ],
                "price": {"base": "85.40", "grandTotal": "170.80", "fees": []},
            }
        ]
    }


def _hotel_payload() -> dict[str, object]:
    return {
        "data": [
            {
                "name": "Hotel Test",
                "hotel": {"rating": "4.2"},
                "offers": [
                    {
                        "id": "hotel-offer-1",
                        "checkInDate": "2026-09-01",
                        "checkOutDate": "2026-09-03",
                        "room": {"typeEstimated": {"category": "DOUBLE_STANDARD"}},
                        "price": {"currency": "EUR", "total": "96.00", "taxes": [{}]},
                        "policies": {"cancellations": [{"deadline": "2026-08-28T23:59:00+02:00"}]},
                        "self": {"href": "https://example.test/hotel-offer-1"},
                    }
                ],
            }
        ]
    }


def test_amadeus_client_refreshes_token_and_get() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path.endswith("/oauth2/token"):
            return httpx.Response(200, json=_TOKEN_RESPONSE)
        if request.url.path.endswith("/v2/shopping/flight-offers"):
            assert request.headers["Authorization"] == "Bearer TOKEN-123"
            return httpx.Response(200, json=_flight_payload())
        return httpx.Response(404)

    client = AmadeusClient(
        "id",
        "secret",
        base_url="https://test.api.amadeus.com",
        transport=httpx.MockTransport(handler),
    )
    response = client.get("/v2/shopping/flight-offers", {"origin": "MAD"})

    assert response.status_code == 200
    assert calls == ["/v1/security/oauth2/token", "/v2/shopping/flight-offers"]
    client.close()


def test_amadeus_client_raises_provider_unavailable_on_http_error() -> None:
    client = AmadeusClient(
        "id",
        "secret",
        base_url="https://test.api.amadeus.com",
        transport=httpx.MockTransport(lambda _: httpx.Response(500)),
    )
    with pytest.raises(ProviderUnavailableError):
        client.get("/v2/shopping/flight-offers", {"origin": "MAD"})
    client.close()


def test_amadeus_flight_provider_normalizes_offers() -> None:
    provider = AmadeusFlightProvider(
        AmadeusClient(
            "id",
            "secret",
            transport=httpx.MockTransport(_token_handler),
        )
    )
    offers = provider.search(
        FlightSearchRequest(
            origin="MAD",
            destination="OPO",
            departure_date="2026-09-01",
            return_date="2026-09-03",
            travelers=2,
        )
    )

    assert len(offers) == 1
    offer = offers[0]
    assert offer.provider == "amadeus"
    assert offer.provider_offer_id == "flight-1"
    assert offer.origin == "MAD"
    assert offer.destination == "OPO"
    assert offer.base_price_eur == 85.4
    assert offer.total_price_eur == 170.8
    assert offer.travelers == 2
    assert offer.departure_at == datetime(2026, 9, 1, 6, 10, tzinfo=UTC)
    assert offer.return_departure_at == datetime(2026, 9, 3, 17, 30, tzinfo=UTC)
    assert offer.verified_at.tzinfo is not None


def test_amadeus_hotel_provider_normalizes_offers() -> None:
    provider = AmadeusHotelProvider(
        AmadeusClient(
            "id",
            "secret",
            transport=httpx.MockTransport(_token_handler),
        )
    )
    offers = provider.search(
        HotelSearchRequest(
            city_code="OPO",
            check_in_date="2026-09-01",
            check_out_date="2026-09-03",
        )
    )

    assert len(offers) == 1
    offer = offers[0]
    assert offer.provider_offer_id == "hotel-offer-1"
    assert offer.hotel_name == "Hotel Test"
    assert offer.total_price_eur == 96.0
    assert offer.currency == "EUR"
    assert offer.taxes_included is True
    assert offer.room_name == "DOUBLE_STANDARD"
    assert offer.free_cancellation_until is not None
    assert offer.booking_url == "https://example.test/hotel-offer-1"


def test_mock_flight_provider_returns_deterministic_offer() -> None:
    provider = MockFlightProvider()
    offers = provider.search(
        FlightSearchRequest(
            origin="MAD",
            destination="OPO",
            departure_date="2026-09-01",
            return_date="2026-09-03",
            travelers=2,
        )
    )

    assert len(offers) == 1
    assert offers[0].total_price_eur == 340.0


def test_mock_hotel_provider_returns_deterministic_offer() -> None:
    provider = MockHotelProvider()
    offers = provider.search(
        HotelSearchRequest(
            city_code="OPO",
            check_in_date="2026-09-01",
            check_out_date="2026-09-03",
        )
    )

    assert len(offers) == 1
    assert offers[0].city_code == "OPO"


def test_build_flight_provider_uses_mock_when_disabled() -> None:
    settings = _amadeus_settings(AMADEUS_ENABLED="false")
    assert isinstance(build_flight_provider(settings), MockFlightProvider)


def test_build_hotel_provider_uses_mock_when_disabled() -> None:
    settings = _amadeus_settings(AMADEUS_ENABLED="false")
    assert isinstance(build_hotel_provider(settings), MockHotelProvider)


def test_build_flight_provider_uses_amadeus_when_enabled() -> None:
    settings = _amadeus_settings()
    assert isinstance(build_flight_provider(settings), AmadeusFlightProvider)


def test_validate_credentials_fails_fast_without_amadeus_credentials() -> None:
    settings = _amadeus_settings(AMADEUS_CLIENT_ID="", AMADEUS_CLIENT_SECRET="")
    with pytest.raises(RuntimeError, match="AMADEUS_CLIENT_ID"):
        settings.validate_provider_credentials()


def test_validate_credentials_passes_when_disabled_without_credentials() -> None:
    settings = _amadeus_settings(AMADEUS_ENABLED="false", AMADEUS_CLIENT_ID="")
    settings.validate_provider_credentials()
