"""Factory for travel provider instances.

The mock providers are the default in development. Real providers are only
built when enabled and their credentials are validated at startup, so the
application never half-starts with a provider that would fail.
"""

from __future__ import annotations

from app.core.config import Settings
from app.providers.amadeus_client import AmadeusClient
from app.providers.amadeus_flight_provider import AmadeusFlightProvider
from app.providers.amadeus_hotel_provider import AmadeusHotelProvider
from app.providers.flight_provider import FlightProvider
from app.providers.hotel_provider import HotelProvider
from app.providers.mock_flight_provider import MockFlightProvider
from app.providers.mock_hotel_provider import MockHotelProvider


def build_flight_provider(settings: Settings) -> FlightProvider:
    """Return the active flight provider for the given settings."""
    if settings.amadeus_enabled:
        return AmadeusFlightProvider(
            AmadeusClient(
                settings.amadeus_client_id,
                settings.amadeus_client_secret,
                base_url=settings.amadeus_base_url,
                timeout_seconds=settings.amadeus_timeout_seconds,
            )
        )
    return MockFlightProvider()


def build_hotel_provider(settings: Settings) -> HotelProvider:
    """Return the active hotel provider for the given settings."""
    if settings.amadeus_enabled:
        return AmadeusHotelProvider(
            AmadeusClient(
                settings.amadeus_client_id,
                settings.amadeus_client_secret,
                base_url=settings.amadeus_base_url,
                timeout_seconds=settings.amadeus_timeout_seconds,
            )
        )
    return MockHotelProvider()
