"""Notification application service.

Coordinates device token registration and sends push notifications derived from
radar alert results. Every attempt is recorded in the notification log with an
explicit status (SENT / SKIPPED / FAILED) so delivery can be audited.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.domain.alerts import AlertRuleCode
from app.domain.enums import NotificationStatus, NotificationType
from app.domain.notification import DeviceRegistration, NotificationLog
from app.domain.search_watch import SearchWatch
from app.providers.device_repository import DeviceRepository
from app.providers.notification_log_repository import NotificationLogRepository
from app.providers.notification_sender import NotificationSender
from app.services.search_watch_service import WatchRunAlert

RADAR_ALERT_DEEP_LINK = "escapa2://radar"


def notification_type_for_rule(rule: str) -> NotificationType:
    """Map a stable alert rule code to a notification type."""
    return {
        AlertRuleCode.NEW_LOW: NotificationType.NEW_LOW,
        AlertRuleCode.NEW_BUDGET_MATCH: NotificationType.BUDGET_MATCH,
        AlertRuleCode.CONSECUTIVE_RISE: NotificationType.PRICE_RISING,
    }.get(rule, NotificationType.PRICE_DROP)


class NotificationService:
    """Handles device registration and push delivery for radar events."""

    def __init__(
        self,
        devices: DeviceRepository,
        sender: NotificationSender,
        logs: NotificationLogRepository,
    ) -> None:
        self._devices = devices
        self._sender = sender
        self._logs = logs

    def register_device(self, user_id: str, token: str, platform: str) -> DeviceRegistration:
        now = datetime.now(UTC).replace(microsecond=0)
        return self._devices.register(
            DeviceRegistration(
                id=uuid.uuid4(),
                user_id=user_id,
                token=token,
                platform=platform,
                created_at=now,
                updated_at=now,
            )
        )

    def unregister_device(self, user_id: str, token: str) -> bool:
        return self._devices.unregister(user_id, token)

    def notify_watch_run(
        self,
        user_id: str,
        watch: SearchWatch,
        alerts: list[WatchRunAlert],
    ) -> list[NotificationLog]:
        """Send notifications for the triggered alerts of a watch run.

        A single message per watch summarizes all triggered alerts and is sent to
        every registered device. Each alert is logged individually with the final
        delivery status.
        """
        if not alerts:
            return []
        tokens = self._devices.list_tokens(user_id)
        if not tokens:
            return [
                self._log(
                    user_id=user_id,
                    watch=watch,
                    alert=alert,
                    status=NotificationStatus.SKIPPED,
                    sent_count=0,
                )
                for alert in alerts
            ]

        title = f"{watch.name}: {len(alerts)} alerta(s)"
        body = " · ".join(alert.message or alert.rule for alert in alerts)
        try:
            sent_count = self._sender.send(
                tokens,
                title[:200],
                body[:500],
                data={
                    "watch_id": str(watch.id),
                    "kind": "RADAR_ALERT",
                    "deep_link": RADAR_ALERT_DEEP_LINK,
                },
            )
        except Exception:  # noqa: BLE001 - delivery failures must not break the radar
            sent_count = 0
        status = NotificationStatus.SENT if sent_count > 0 else NotificationStatus.FAILED
        return [
            self._log(
                user_id=user_id,
                watch=watch,
                alert=alert,
                status=status,
                sent_count=sent_count,
            )
            for alert in alerts
        ]

    def _log(
        self,
        *,
        user_id: str,
        watch: SearchWatch,
        alert: WatchRunAlert,
        status: NotificationStatus,
        sent_count: int,
    ) -> NotificationLog:
        return self._logs.add(
            NotificationLog(
                id=uuid.uuid4(),
                user_id=user_id,
                search_watch_id=watch.id,
                type=notification_type_for_rule(alert.rule),
                title=f"{watch.name}: {alert.message or alert.rule}",
                body=alert.message or alert.rule,
                payload_json={"rule": alert.rule, "sent_count": sent_count},
                sent_at=datetime.now(UTC).replace(microsecond=0),
                status=status,
            )
        )
