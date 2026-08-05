"""Normalized domain models for availability windows."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, model_validator

from app.domain.enums import WindowKind


class AvailabilityWindow(BaseModel):
    """A time range during which the couple can travel."""

    id: uuid.UUID
    start_at: datetime
    end_at: datetime
    kind: WindowKind = WindowKind.WEEKEND
    is_flexible: bool = False
    created_at: datetime

    @model_validator(mode="after")
    def _validate_window(self) -> AvailabilityWindow:
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self
