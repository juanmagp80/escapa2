"""Availability window application service.

Applies business rules on top of the availability provider: input validation,
window range consistency and existence checks.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, model_validator

from app.core.errors import NotFoundError
from app.domain.availability import AvailabilityWindow
from app.domain.enums import WindowKind
from app.providers.availability_provider import AvailabilityProvider


class AvailabilityCreate(BaseModel):
    """Fields accepted by POST /availability."""

    start_at: datetime
    end_at: datetime
    kind: WindowKind = WindowKind.WEEKEND
    is_flexible: bool = False

    @model_validator(mode="after")
    def _validate_window(self) -> AvailabilityCreate:
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self


class AvailabilityUpdate(BaseModel):
    """Fields accepted by PUT /availability/{id}."""

    start_at: datetime
    end_at: datetime
    kind: WindowKind = WindowKind.WEEKEND
    is_flexible: bool = False

    @model_validator(mode="after")
    def _validate_window(self) -> AvailabilityUpdate:
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self


class AvailabilityService:
    """Application service exposing availability operations."""

    def __init__(self, provider: AvailabilityProvider) -> None:
        self._provider = provider

    def list(self) -> list[AvailabilityWindow]:
        return self._provider.list_windows()

    def get(self, window_id: uuid.UUID) -> AvailabilityWindow:
        window = self._provider.get_window(window_id)
        if window is None:
            raise NotFoundError("availability window", str(window_id))
        return window

    def create(self, data: AvailabilityCreate) -> AvailabilityWindow:
        window = AvailabilityWindow(
            id=uuid.uuid4(),
            start_at=data.start_at,
            end_at=data.end_at,
            kind=data.kind,
            is_flexible=data.is_flexible,
            created_at=datetime.now(UTC),
        )
        return self._provider.create_window(window)

    def update(self, window_id: uuid.UUID, data: AvailabilityUpdate) -> AvailabilityWindow:
        current = self.get(window_id)
        updated = current.model_copy(
            update={
                "start_at": data.start_at,
                "end_at": data.end_at,
                "kind": data.kind,
                "is_flexible": data.is_flexible,
            }
        )
        return self._provider.update_window(updated)

    def delete(self, window_id: uuid.UUID) -> None:
        if not self._provider.delete_window(window_id):
            raise NotFoundError("availability window", str(window_id))
