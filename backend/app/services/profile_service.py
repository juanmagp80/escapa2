"""Travel profile application service.

Applies business rules on top of the profile provider: input validation,
preservation of immutable fields and airport replacement semantics.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.enums import TransportMode
from app.domain.profile import AirportPreference, TravelProfile
from app.providers.profile_provider import ProfileProvider


class ProfileUpdate(BaseModel):
    """Mutable fields accepted by PUT /profile."""

    origin_city: str = Field(..., min_length=1, max_length=120)
    currency: str = Field(..., min_length=3, max_length=3)
    default_budget_eur: float | None = Field(default=None, ge=0)
    max_drive_minutes: int | None = Field(default=None, ge=0)
    preferred_transport: TransportMode = TransportMode.EITHER
    interests: list[str] = Field(default_factory=list, max_length=30)
    avoid_preferences: list[str] = Field(default_factory=list, max_length=30)

    @field_validator("currency")
    @classmethod
    def _uppercase_currency(cls, value: str) -> str:
        return value.strip().upper()

    @model_validator(mode="after")
    def _clean_preference_lists(self) -> ProfileUpdate:
        self.interests = _clean_strings(self.interests)
        self.avoid_preferences = _clean_strings(self.avoid_preferences)
        return self


class AirportPreferenceInput(BaseModel):
    """One airport accepted by PUT /profile/airports."""

    iata_code: str = Field(..., min_length=3, max_length=3)
    enabled: bool = True
    transfer_cost_eur: float | None = Field(default=None, ge=0)
    transfer_minutes: int | None = Field(default=None, ge=0)

    @field_validator("iata_code")
    @classmethod
    def _uppercase_iata(cls, value: str) -> str:
        return value.strip().upper()


def _clean_strings(values: list[str]) -> list[str]:
    return [value.strip() for value in values if value.strip()]


class ProfileService:
    """Application service exposing profile operations."""

    def __init__(self, provider: ProfileProvider) -> None:
        self._provider = provider

    def get(self) -> TravelProfile:
        return self._provider.get_profile()

    def update(self, changes: ProfileUpdate) -> TravelProfile:
        current = self._provider.get_profile()
        updated = current.model_copy(
            update={
                "origin_city": changes.origin_city.strip(),
                "currency": changes.currency,
                "default_budget_eur": changes.default_budget_eur,
                "max_drive_minutes": changes.max_drive_minutes,
                "preferred_transport": changes.preferred_transport,
                "interests": changes.interests,
                "avoid_preferences": changes.avoid_preferences,
                "updated_at": datetime.now(UTC),
            }
        )
        return self._provider.save_profile(updated)

    def get_airports(self) -> list[AirportPreference]:
        return self._provider.get_airports()

    def replace_airports(self, inputs: list[AirportPreferenceInput]) -> list[AirportPreference]:
        profile = self._provider.get_profile()
        airports = [
            AirportPreference(
                id=uuid.uuid4(),
                travel_profile_id=profile.id,
                iata_code=airport.iata_code,
                enabled=airport.enabled,
                transfer_cost_eur=airport.transfer_cost_eur,
                transfer_minutes=airport.transfer_minutes,
            )
            for airport in inputs
        ]
        return self._provider.save_airports(airports)
