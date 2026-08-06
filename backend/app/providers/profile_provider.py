"""Travel profile provider contract."""

from __future__ import annotations

from typing import Protocol

from app.domain.profile import AirportPreference, TravelProfile
from app.domain.vehicles import VehicleProfile


class ProfileProvider(Protocol):
    """Contract for sources that persist the couple travel profile."""

    def get_profile(self) -> TravelProfile:
        """Return the current profile."""
        ...

    def save_profile(self, profile: TravelProfile) -> TravelProfile:
        """Persist the profile and return the stored value."""
        ...

    def get_airports(self) -> list[AirportPreference]:
        """Return the enabled departure airports."""
        ...

    def save_airports(self, airports: list[AirportPreference]) -> list[AirportPreference]:
        """Replace the airport preferences and return the stored value."""
        ...

    def get_vehicle(self) -> VehicleProfile:
        """Return the default vehicle of the couple."""
        ...

    def save_vehicle(self, vehicle: VehicleProfile) -> VehicleProfile:
        """Persist the default vehicle and return the stored value."""
        ...
