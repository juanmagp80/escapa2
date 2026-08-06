"""Notification log repository contract."""

from __future__ import annotations

from typing import Protocol

from app.domain.notification import NotificationLog


class NotificationLogRepository(Protocol):
    """Contract for persisting notification delivery attempts."""

    def add(self, log: NotificationLog) -> NotificationLog:
        """Persist a notification attempt."""
        ...

    def list_for_user(self, user_id: str) -> list[NotificationLog]:
        """Return recent notifications for a user, newest first."""
        ...
