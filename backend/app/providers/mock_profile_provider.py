"""In-memory provider with a development profile for the vertical slice."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.domain.enums import TransportMode
from app.domain.profile import AirportPreference, TravelProfile

_DEV_PROFILE_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")


def _utc_now() -> datetime:
    return datetime.now(UTC)


class MockProfileProvider:
    """Serves a single development profile until persistence is added."""

    def __init__(self) -> None:
        now = _utc_now()
        self._profile = TravelProfile(
            id=_DEV_PROFILE_ID,
            origin_city="Madrid",
            currency="EUR",
            default_budget_eur=350.0,
            max_drive_minutes=240,
            preferred_transport=TransportMode.EITHER,
            interests=["ciudad", "gastronomía"],
            avoid_preferences=["vida nocturna"],
            created_at=now,
            updated_at=now,
        )
        self._airports: list[AirportPreference] = [
            AirportPreference(
                id=uuid.UUID("00000000-0000-4000-8000-000000000002"),
                travel_profile_id=_DEV_PROFILE_ID,
                iata_code="MAD",
                enabled=True,
                transfer_cost_eur=12.0,
                transfer_minutes=45,
            ),
            AirportPreference(
                id=uuid.UUID("00000000-0000-4000-8000-000000000003"),
                travel_profile_id=_DEV_PROFILE_ID,
                iata_code="BCN",
                enabled=False,
                transfer_cost_eur=0.0,
                transfer_minutes=30,
            ),
        ]

    def get_profile(self) -> TravelProfile:
        return self._profile.model_copy(deep=True)

    def save_profile(self, profile: TravelProfile) -> TravelProfile:
        self._profile = profile.model_copy(deep=True)
        return self._profile.model_copy(deep=True)

    def get_airports(self) -> list[AirportPreference]:
        return [airport.model_copy(deep=True) for airport in self._airports]

    def save_airports(self, airports: list[AirportPreference]) -> list[AirportPreference]:
        self._airports = [airport.model_copy(deep=True) for airport in airports]
        return self.get_airports()
