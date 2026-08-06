"""Firebase Cloud Messaging sender, only used when Firebase is enabled.

The ``firebase-admin`` SDK is imported lazily so the rest of the system runs
without it; if Firebase is enabled but the SDK or credentials are missing, a
clear error is raised instead of failing silently.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.errors import ProviderUnavailableError

logger = logging.getLogger(__name__)


class FirebaseNotificationSender:
    """Sends push notifications through Firebase Cloud Messaging."""

    def __init__(
        self,
        project_id: str,
        credentials_file: str = "",
        credentials_json: str = "",
    ) -> None:
        self._project_id = project_id
        self._credentials_file = credentials_file
        self._credentials_json = credentials_json
        self._app: Any | None = None

    def send(
        self,
        device_tokens: list[str],
        title: str,
        body: str,
        *,
        data: dict[str, str] | None = None,
    ) -> int:
        if not device_tokens:
            return 0
        messaging, app = self._initialize()
        message = messaging.MulticastMessage(
            tokens=device_tokens,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
        )
        try:
            response = messaging.send_each_for_multicast(message, app=app)
        except Exception as exc:  # noqa: BLE001 - map any SDK error
            logger.warning("Firebase send failed: %s", exc)
            raise ProviderUnavailableError() from exc
        success = int(response.success_count)
        if success < len(device_tokens):
            logger.warning(
                "Firebase partial delivery: %s/%s succeeded", success, len(device_tokens)
            )
        return success

    def _initialize(self) -> tuple[Any, Any]:
        if self._app is not None:
            import firebase_admin.messaging as messaging  # type: ignore[import-not-found]

            return messaging, self._app
        try:
            import firebase_admin
            import firebase_admin.messaging as messaging
        except ImportError as exc:  # pragma: no cover - depends on optional dependency
            raise RuntimeError("FIREBASE_ENABLED=true requires the firebase-admin package") from exc
        app = firebase_admin.initialize_app(
            self._build_credentials(firebase_admin),
            options={"projectId": self._project_id},
        )
        self._app = app
        return messaging, app

    def _build_credentials(self, firebase_admin: Any) -> Any:
        if self._credentials_json:
            return firebase_admin.credentials.Certificate(json.loads(self._credentials_json))
        return firebase_admin.credentials.Certificate(self._credentials_file)
