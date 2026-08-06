"""No-op push sender used when Firebase is disabled or in tests."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class MockNotificationSender:
    """Accepts notifications and only logs them (dev/tests default)."""

    def send(
        self,
        device_tokens: list[str],
        title: str,
        body: str,
        *,
        data: dict[str, str] | None = None,
    ) -> int:
        logger.info("Mock notification (devices=%s) %s: %s", len(device_tokens), title, body)
        return len(device_tokens)
