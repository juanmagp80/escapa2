"""Tests for the radar scheduler selection and run loop."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from app.domain.enums import WatchStatus
from app.domain.search_watch import SearchWatch
from app.providers.mock_opportunity_provider import MockOpportunityProvider
from app.services.radar_scheduler import RadarScheduler, due_watches
from app.services.search_watch_service import SearchWatchService


def _watch(
    *,
    watch_id: str,
    status: WatchStatus = WatchStatus.ACTIVE,
    next_run_at: datetime | None = None,
) -> SearchWatch:
    now = datetime.now(UTC)
    return SearchWatch(
        id=uuid.UUID(watch_id),
        couple_id=uuid.UUID("00000000-0000-4000-8000-000000000001"),
        name="Watch",
        status=status,
        next_run_at=next_run_at,
        created_at=now,
        updated_at=now,
    )


class StubWatchProvider:
    """Deterministic in-memory provider with an explicit watch set."""

    def __init__(self, watches: list[SearchWatch]) -> None:
        self._watches = list(watches)

    def list_watches(self) -> list[SearchWatch]:
        return [watch.model_copy(deep=True) for watch in self._watches]

    def get_watch(self, watch_id: uuid.UUID) -> SearchWatch | None:
        watch = next((item for item in self._watches if item.id == watch_id), None)
        return watch.model_copy(deep=True) if watch is not None else None

    def create_watch(self, watch: SearchWatch) -> SearchWatch:
        stored = watch.model_copy(deep=True)
        self._watches.append(stored)
        return stored.model_copy(deep=True)

    def update_watch(self, watch: SearchWatch) -> SearchWatch:
        for index, current in enumerate(self._watches):
            if current.id == watch.id:
                self._watches[index] = watch.model_copy(deep=True)
                return self._watches[index].model_copy(deep=True)
        raise KeyError(f"watch '{watch.id}' not found")

    def delete_watch(self, watch_id: uuid.UUID) -> bool:
        for index, current in enumerate(self._watches):
            if current.id == watch_id:
                del self._watches[index]
                return True
        return False


def test_due_watches_filters_by_status_and_schedule() -> None:
    now = datetime.now(UTC)
    active_due = _watch(
        watch_id="10000000-0000-4000-8000-000000000001",
        next_run_at=now - timedelta(hours=1),
    )
    active_future = _watch(
        watch_id="10000000-0000-4000-8000-000000000002",
        next_run_at=now + timedelta(hours=1),
    )
    active_never = _watch(watch_id="10000000-0000-4000-8000-000000000003", next_run_at=None)
    paused_due = _watch(
        watch_id="10000000-0000-4000-8000-000000000004",
        status=WatchStatus.PAUSED,
        next_run_at=now - timedelta(hours=1),
    )

    due = due_watches([active_due, active_future, active_never, paused_due], now)

    assert due == [active_due, active_never]


def test_due_watches_ignores_empty_list() -> None:
    assert due_watches([], datetime.now(UTC)) == []


def test_run_due_executes_due_watches_only() -> None:
    now = datetime.now(UTC)
    provider = StubWatchProvider(
        [
            _watch(
                watch_id="10000000-0000-4000-8000-000000000001",
                next_run_at=now - timedelta(hours=1),
            ),
            _watch(
                watch_id="10000000-0000-4000-8000-000000000002",
                next_run_at=now + timedelta(hours=1),
            ),
        ]
    )
    service = SearchWatchService(provider, MockOpportunityProvider())

    scheduler = RadarScheduler(service, interval_seconds=60)
    executed = scheduler.run_due()

    assert executed == 1
    due_after = provider.get_watch(uuid.UUID("10000000-0000-4000-8000-000000000001"))
    assert due_after is not None
    assert due_after.last_run_at is not None
    assert due_after.next_run_at > now
    future_after = provider.get_watch(uuid.UUID("10000000-0000-4000-8000-000000000002"))
    assert future_after is not None
    assert future_after.last_run_at is None


def test_run_due_keeps_going_when_one_watch_fails() -> None:
    now = datetime.now(UTC)
    provider = StubWatchProvider(
        [
            _watch(
                watch_id="10000000-0000-4000-8000-000000000001",
                next_run_at=now - timedelta(hours=1),
            ),
            _watch(
                watch_id="10000000-0000-4000-8000-000000000002",
                next_run_at=now - timedelta(hours=1),
            ),
        ]
    )
    failing_ids = {uuid.UUID("10000000-0000-4000-8000-000000000001")}

    class FailingService(SearchWatchService):
        def run(self, watch_id: uuid.UUID):
            if watch_id in failing_ids:
                raise RuntimeError("provider unavailable")
            return super().run(watch_id)

    scheduler = RadarScheduler(
        FailingService(provider, MockOpportunityProvider()),
        interval_seconds=60,
    )
    executed = scheduler.run_due()

    assert executed == 2
    second = provider.get_watch(uuid.UUID("10000000-0000-4000-8000-000000000002"))
    assert second is not None
    assert second.last_run_at is not None
