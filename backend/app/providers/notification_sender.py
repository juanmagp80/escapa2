"""Push notification sender contract.

The radar and services depend on this protocol, never on Firebase directly, so
the system works without Firebase (mock sender) and tests never touch the real
push service.
"""

from __future__ import annotations

from typing import Protocol


class NotificationSender(Protocol):
    """Contract for sending push notifications to device tokens."""

    def send(
        self,
        device_tokens: list[str],
        title: str,
        body: str,
        *,
        data: dict[str, str] | None = None,
    ) -> int:
        """Send a notification and return how many devices accepted it."""
        ...
