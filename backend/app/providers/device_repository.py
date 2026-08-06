"""Device token registry contract."""

from __future__ import annotations

from typing import Protocol

from app.domain.notification import DeviceRegistration


class DeviceRepository(Protocol):
    """Contract for storing push device tokens."""

    def list_tokens(self, user_id: str) -> list[str]:
        """Return the push tokens registered for a user."""
        ...

    def register(self, device: DeviceRegistration) -> DeviceRegistration:
        """Register a device; idempotent by token."""
        ...

    def unregister(self, user_id: str, token: str) -> bool:
        """Remove a device token; return whether it existed."""
        ...
