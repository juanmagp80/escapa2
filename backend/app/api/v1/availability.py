"""Availability API under the /api/v1/availability prefix."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_availability_service
from app.domain.availability import AvailabilityWindow
from app.services.availability_service import (
    AvailabilityCreate,
    AvailabilityService,
    AvailabilityUpdate,
)

router = APIRouter(prefix="/availability", tags=["availability"])

AvailabilityServiceDep = Annotated[AvailabilityService, Depends(get_availability_service)]


@router.get("", response_model=list[AvailabilityWindow])
def list_windows(service: AvailabilityServiceDep) -> list[AvailabilityWindow]:
    """Return all availability windows."""
    return service.list()


@router.post("", response_model=AvailabilityWindow, status_code=status.HTTP_201_CREATED)
def create_window(
    data: AvailabilityCreate,
    service: AvailabilityServiceDep,
) -> AvailabilityWindow:
    """Create a new availability window."""
    return service.create(data)


@router.put("/{window_id}", response_model=AvailabilityWindow)
def update_window(
    window_id: uuid.UUID,
    data: AvailabilityUpdate,
    service: AvailabilityServiceDep,
) -> AvailabilityWindow:
    """Replace the mutable fields of an availability window."""
    return service.update(window_id, data)


@router.delete("/{window_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_window(
    window_id: uuid.UUID,
    service: AvailabilityServiceDep,
    response: Response,
) -> None:
    """Delete an availability window."""
    service.delete(window_id)
    response.status_code = status.HTTP_204_NO_CONTENT
