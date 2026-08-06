"""In-memory fuel-price provider with simulated stations for development and tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.domain.offers import FuelStation, FuelStationsRequest


def _station(*, station_id: str, name: str, price: float, lat: float, lon: float) -> FuelStation:
    now = datetime.now(UTC).replace(microsecond=0)
    return FuelStation(
        station_id=station_id,
        name=name,
        brand=None,
        latitude=lat,
        longitude=lon,
        price_per_liter_eur=round(price, 3),
        fuels_available=["DIESEL", "GASOLINE"],
        last_updated=now,
    )


class MockFuelPriceProvider:
    """Serves deterministic fuel stations without calling the official API."""

    def stations_near_route(self, request: FuelStationsRequest) -> list[FuelStation]:
        # Two reference stations with distinct prices; order is deterministic.
        return [
            _station(
                station_id="ES001",
                name="Gasolinera Central",
                price=1.525,
                lat=40.4168,
                lon=-3.7038,
            ),
            _station(
                station_id="ES002",
                name="Gasolinera Avenida",
                price=1.485,
                lat=40.42,
                lon=-3.71,
            ),
        ]
