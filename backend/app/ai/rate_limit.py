"""In-memory rate limiting for AI requests per user and day."""

from __future__ import annotations

from datetime import UTC, datetime

from app.core.errors import RateLimitedError


class AiRateLimiter:
    """Tracks AI requests per user key and UTC day."""

    def __init__(self, max_requests_per_day: int) -> None:
        self._max_requests_per_day = max_requests_per_day
        self._counts: dict[tuple[str, str], int] = {}

    def _day_key(self) -> str:
        return datetime.now(UTC).date().isoformat()

    def remaining(self, user_key: str) -> int:
        """Requests the user can still make today, without consuming quota."""
        key = (user_key, self._day_key())
        used = self._counts.get(key, 0)
        return max(0, self._max_requests_per_day - used)

    def check_and_consume(self, user_key: str) -> None:
        """Consume one request or raise RateLimitedError when the quota is gone."""
        key = (user_key, self._day_key())
        used = self._counts.get(key, 0)
        if used >= self._max_requests_per_day:
            raise RateLimitedError()
        self._counts[key] = used + 1

    def reset(self) -> None:
        self._counts.clear()
