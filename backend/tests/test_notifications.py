"""Tests for the notification layer: device registry, service and endpoints."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.domain.alerts import AlertRuleCode
from app.domain.enums import NotificationStatus, NotificationType
from app.domain.search_watch import SearchWatch
from app.providers.mock_device_repository import MockDeviceRepository
from app.providers.mock_notification_log_repository import MockNotificationLogRepository
from app.services.notification_service import (
    NotificationService,
    notification_type_for_rule,
)
from app.services.search_watch_service import WatchRunAlert
from fastapi.testclient import TestClient


class RecordingSender:
    """Records delivered notifications for assertions."""

    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str, str]] = []
        self.fail = False

    def send(
        self,
        device_tokens: list[str],
        title: str,
        body: str,
        *,
        data: dict[str, str] | None = None,
    ) -> int:
        if self.fail:
            raise RuntimeError("push backend down")
        self.calls.append((list(device_tokens), title, body))
        return len(device_tokens)


def _watch(*, watch_id: str = "11111111-1111-4111-8111-111111111111") -> SearchWatch:
    now = datetime.now(UTC)
    return SearchWatch(
        id=uuid.UUID(watch_id),
        couple_id=uuid.UUID("00000000-0000-4000-8000-000000000001"),
        name="Porto en avión",
        status="ACTIVE",
        created_at=now,
        updated_at=now,
    )


def _alerts() -> list[WatchRunAlert]:
    return [WatchRunAlert(rule=AlertRuleCode.NEW_LOW, message="Nuevo mínimo histórico: 312 EUR")]


def test_notification_type_for_rule_mapping() -> None:
    assert notification_type_for_rule(AlertRuleCode.NEW_LOW) == NotificationType.NEW_LOW
    assert (
        notification_type_for_rule(AlertRuleCode.NEW_BUDGET_MATCH) == NotificationType.BUDGET_MATCH
    )
    assert (
        notification_type_for_rule(AlertRuleCode.CONSECUTIVE_RISE) == NotificationType.PRICE_RISING
    )
    assert notification_type_for_rule(AlertRuleCode.PERCENT_DROP) == NotificationType.PRICE_DROP


def test_register_device_is_idempotent() -> None:
    repository = MockDeviceRepository()
    service = NotificationService(repository, RecordingSender(), MockNotificationLogRepository())

    first = service.register_device("dev-user", "token-abc-123", "android")
    second = service.register_device("dev-user", "token-abc-123", "android")

    assert first.token == second.token
    assert repository.list_tokens("dev-user") == ["token-abc-123"]


def test_unregister_device_removes_token() -> None:
    repository = MockDeviceRepository()
    service = NotificationService(repository, RecordingSender(), MockNotificationLogRepository())
    service.register_device("dev-user", "token-abc-123", "android")

    assert service.unregister_device("dev-user", "token-abc-123") is True
    assert service.unregister_device("dev-user", "token-abc-123") is False
    assert repository.list_tokens("dev-user") == []


def test_notify_watch_run_sends_and_logs() -> None:
    devices = MockDeviceRepository()
    sender = RecordingSender()
    logs = MockNotificationLogRepository()
    service = NotificationService(devices, sender, logs)
    service.register_device("dev-user", "token-abc-123", "android")
    watch = _watch()

    entries = service.notify_watch_run("dev-user", watch, _alerts())

    assert len(sender.calls) == 1
    assert sender.calls[0][0] == ["token-abc-123"]
    assert "Porto en avión" in sender.calls[0][1]
    assert len(entries) == 1
    assert entries[0].status == NotificationStatus.SENT
    assert entries[0].type == NotificationType.NEW_LOW
    assert entries[0].search_watch_id == watch.id
    assert logs.list_for_user("dev-user")[0].status == NotificationStatus.SENT


def test_notify_watch_run_skips_when_no_devices() -> None:
    sender = RecordingSender()
    logs = MockNotificationLogRepository()
    service = NotificationService(MockDeviceRepository(), sender, logs)

    entries = service.notify_watch_run("dev-user", _watch(), _alerts())

    assert sender.calls == []
    assert entries[0].status == NotificationStatus.SKIPPED
    assert logs.list_for_user("dev-user")[0].status == NotificationStatus.SKIPPED


def test_notify_watch_run_marks_failed_when_sender_raises() -> None:
    devices = MockDeviceRepository()
    sender = RecordingSender()
    sender.fail = True
    logs = MockNotificationLogRepository()
    service = NotificationService(devices, sender, logs)
    service.register_device("dev-user", "token-abc-123", "android")

    entries = service.notify_watch_run("dev-user", _watch(), _alerts())

    assert entries[0].status == NotificationStatus.FAILED


def test_notify_watch_run_no_alerts_returns_empty() -> None:
    service = NotificationService(
        MockDeviceRepository(), RecordingSender(), MockNotificationLogRepository()
    )
    assert service.notify_watch_run("dev-user", _watch(), []) == []


def test_devices_endpoint_registers_and_unregisters(client: TestClient) -> None:
    response = client.post(
        "/api/v1/devices", json={"token": "device-token-123", "platform": "android"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["token"] == "device-token-123"  # noqa: S105
    assert body["platform"] == "android"

    deleted = client.delete("/api/v1/devices/device-token-123")
    assert deleted.status_code == 204


def test_devices_endpoint_rejects_invalid_token(client: TestClient) -> None:
    response = client.post("/api/v1/devices", json={"token": "short"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_radar_scheduler_notifies_after_run() -> None:
    from app.providers.mock_opportunity_provider import MockOpportunityProvider
    from app.providers.mock_search_watch_provider import MockSearchWatchProvider
    from app.services.radar_scheduler import DEV_USER_ID, RadarScheduler
    from app.services.search_watch_service import SearchWatchCreate, SearchWatchService

    devices = MockDeviceRepository()
    sender = RecordingSender()
    service = NotificationService(devices, sender, MockNotificationLogRepository())
    service.register_device(DEV_USER_ID, "token-abc-123", "android")

    watch_service = SearchWatchService(MockSearchWatchProvider(), MockOpportunityProvider())
    watch_service.create(
        SearchWatchCreate.model_validate(
            {
                "name": "Roma en avión",
                "criteria": {"max_total_cost_eur": 400, "transport_mode": "FLIGHT"},
                "alert_rules": {"rules": ["Nuevo mínimo histórico"]},
            }
        )
    )

    scheduler = RadarScheduler(
        watch_service,
        interval_seconds=60.0,
        notifications=service,
    )
    ran = scheduler.run_due()

    assert ran >= 1
    assert sender.calls, "expected a notification to be sent for the triggered alert"
