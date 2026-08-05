"""Travel profile provider contract."""

from __future__ import annotations

from typing import Protocol

from app.domain.profile import AirportPreference, TravelProfile


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
