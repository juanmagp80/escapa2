"""In-memory notification log for development and tests."""

from __future__ import annotations

from app.domain.notification import NotificationLog


class MockNotificationLogRepository:
    """Keeps notification attempts in memory."""

    def __init__(self) -> None:
        self._logs: list[NotificationLog] = []

    def add(self, log: NotificationLog) -> NotificationLog:
        self._logs.append(log)
        return log

    def list_for_user(self, user_id: str) -> list[NotificationLog]:
        return [log for log in reversed(self._logs) if log.user_id == user_id]
