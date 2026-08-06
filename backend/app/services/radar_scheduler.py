"""Radar scheduler.

Runs the configured daily radar in a background thread: every interval it
selects active watches whose ``next_run_at`` has passed and executes them
through ``SearchWatchService.run``, which refreshes the schedule, records price
snapshots and evaluates the configured alert rules.

The scheduler is disabled by default (``SCHEDULER_ENABLED=false``) and is never
started automatically in tests. The pure selection logic lives in
``due_watches`` so it can be unit tested without threads.
"""

from __future__ import annotations

import logging
import threading
from datetime import UTC, datetime

from app.domain.enums import WatchStatus
from app.domain.search_watch import SearchWatch
from app.services.notification_service import NotificationService
from app.services.search_watch_service import SearchWatchService, WatchRunAlert

logger = logging.getLogger(__name__)

DEV_USER_ID = "dev-user"


def due_watches(watches: list[SearchWatch], now: datetime) -> list[SearchWatch]:
    """Return the active watches that are due to run at ``now``."""
    return [
        watch
        for watch in watches
        if watch.status == WatchStatus.ACTIVE
        and (watch.next_run_at is None or watch.next_run_at <= now)
    ]


class RadarScheduler:
    """Background loop that runs due watches at a fixed interval."""

    def __init__(
        self,
        service: SearchWatchService,
        interval_seconds: float,
        notifications: NotificationService | None = None,
    ) -> None:
        self._service = service
        self._interval_seconds = interval_seconds
        self._notifications = notifications
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.running:
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop,
            name="escapa2-radar-scheduler",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "Radar scheduler started (interval=%ss)",
            self._interval_seconds,
        )

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
        logger.info("Radar scheduler stopped")

    def run_due(self) -> int:
        """Execute all currently due watches; return how many ran."""
        now = datetime.now(UTC)
        due = due_watches(self._service.list_watches(), now)
        for watch in due:
            try:
                result = self._service.run(watch.id)
                logger.info(
                    "Radar run watch=%s matches=%s alerts=%s",
                    watch.id,
                    len(result.matched_opportunities),
                    len(result.alerts),
                )
                self._notify(watch, result.alerts)
            except Exception:  # noqa: BLE001 - keep the loop alive
                logger.exception("Radar run failed for watch=%s", watch.id)
        return len(due)

    def _notify(self, watch: SearchWatch, alerts: list[WatchRunAlert]) -> None:
        if self._notifications is None or not alerts:
            return
        try:
            self._notifications.notify_watch_run(DEV_USER_ID, watch, alerts)
        except Exception:  # noqa: BLE001 - notifications must not break the radar
            logger.exception("Notification delivery failed for watch=%s", watch.id)

    def _loop(self) -> None:
        while not self._stop.wait(self._interval_seconds):
            self.run_due()
