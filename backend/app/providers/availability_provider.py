"""Availability window provider contract."""

from __future__ import annotations

import uuid
from typing import Protocol

from app.domain.availability import AvailabilityWindow


class AvailabilityProvider(Protocol):
    """Contract for sources that persist availability windows."""

    def list_windows(self) -> list[AvailabilityWindow]:
        """Return all availability windows."""
        ...

    def get_window(self, window_id: uuid.UUID) -> AvailabilityWindow | None:
        """Return a single window or None when unknown."""
        ...

    def create_window(self, window: AvailabilityWindow) -> AvailabilityWindow:
        """Store a new window and return the stored value."""
        ...

    def update_window(self, window: AvailabilityWindow) -> AvailabilityWindow:
        """Store an updated window and return the stored value."""
        ...

    def delete_window(self, window_id: uuid.UUID) -> bool:
        """Delete a window; return True when it existed."""
        ...
