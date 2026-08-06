"""In-memory provider with development search watches."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from app.domain.enums import WatchStatus
from app.domain.search_watch import SearchWatch

COUPLE_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")


class MockSearchWatchProvider:
    """Serves a small set of watched searches until persistence is added."""

    def __init__(self) -> None:
        now = datetime.now(UTC)
        self._watches: list[SearchWatch] = [
            SearchWatch(
                id=uuid.UUID("20000000-0000-4000-8000-000000000001"),
                couple_id=COUPLE_ID,
                name="Porto en avión",
                status=WatchStatus.ACTIVE,
                criteria_json={"initial_price_eur": 312.0},
                alert_rules_json={
                    "rules": ["Nuevo mínimo histórico", "Viaje por debajo de 350 EUR"]
                },
                last_run_at=now - timedelta(days=1),
                next_run_at=now,
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(days=1),
            ),
            SearchWatch(
                id=uuid.UUID("20000000-0000-4000-8000-000000000002"),
                couple_id=COUPLE_ID,
                name="Galicia en coche",
                status=WatchStatus.ACTIVE,
                criteria_json={"initial_price_eur": 198.0},
                alert_rules_json={"rules": ["Bajada superior a 10%"]},
                last_run_at=now - timedelta(days=1),
                next_run_at=now,
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(days=1),
            ),
        ]

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
