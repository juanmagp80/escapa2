"""Travel profile API under the /api/v1/profile prefix."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_profile_service
from app.domain.profile import AirportPreference, TravelProfile
from app.services.profile_service import (
    AirportPreferenceInput,
    ProfileService,
    ProfileUpdate,
)

router = APIRouter(prefix="/profile", tags=["profile"])

ProfileServiceDep = Annotated[ProfileService, Depends(get_profile_service)]


@router.get("", response_model=TravelProfile)
def get_profile(service: ProfileServiceDep) -> TravelProfile:
    """Return the couple travel profile."""
    return service.get()


@router.put("", response_model=TravelProfile)
def update_profile(
    changes: ProfileUpdate,
    service: ProfileServiceDep,
) -> TravelProfile:
    """Replace the mutable fields of the travel profile."""
    return service.update(changes)


@router.get("/airports", response_model=list[AirportPreference])
def get_airports(service: ProfileServiceDep) -> list[AirportPreference]:
    """Return the accepted departure airports."""
    return service.get_airports()


@router.put("/airports", response_model=list[AirportPreference])
def replace_airports(
    airports: list[AirportPreferenceInput],
    service: ProfileServiceDep,
) -> list[AirportPreference]:
    """Replace the full list of accepted departure airports."""
    return service.replace_airports(airports)
