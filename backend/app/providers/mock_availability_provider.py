"""In-memory provider with development availability windows."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.domain.availability import AvailabilityWindow
from app.domain.enums import WindowKind


def _utc(iso: str) -> datetime:
    return datetime.fromisoformat(iso).astimezone(UTC)


class MockAvailabilityProvider:
    """Serves a small set of availability windows until persistence is added."""

    def __init__(self) -> None:
        now = datetime.now(UTC)
        self._windows: list[AvailabilityWindow] = [
            AvailabilityWindow(
                id=uuid.UUID("10000000-0000-4000-8000-000000000001"),
                start_at=_utc("2026-08-14T18:00:00+02:00"),
                end_at=_utc("2026-08-16T22:00:00+02:00"),
                kind=WindowKind.WEEKEND,
                is_flexible=True,
                created_at=now,
            ),
            AvailabilityWindow(
                id=uuid.UUID("10000000-0000-4000-8000-000000000002"),
                start_at=_utc("2026-08-21T18:00:00+02:00"),
                end_at=_utc("2026-08-23T22:00:00+02:00"),
                kind=WindowKind.WEEKEND,
                is_flexible=False,
                created_at=now,
            ),
            AvailabilityWindow(
                id=uuid.UUID("10000000-0000-4000-8000-000000000003"),
                start_at=_utc("2026-09-28T00:00:00+02:00"),
                end_at=_utc("2026-10-04T23:59:00+02:00"),
                kind=WindowKind.VACATION,
                is_flexible=True,
                created_at=now,
            ),
        ]

    def list_windows(self) -> list[AvailabilityWindow]:
        return [window.model_copy(deep=True) for window in self._windows]

    def get_window(self, window_id: uuid.UUID) -> AvailabilityWindow | None:
        window = next(
            (item for item in self._windows if item.id == window_id),
            None,
        )
        return window.model_copy(deep=True) if window is not None else None

    def create_window(self, window: AvailabilityWindow) -> AvailabilityWindow:
        stored = window.model_copy(deep=True)
        self._windows.append(stored)
        return stored.model_copy(deep=True)

    def update_window(self, window: AvailabilityWindow) -> AvailabilityWindow:
        for index, current in enumerate(self._windows):
            if current.id == window.id:
                self._windows[index] = window.model_copy(deep=True)
                return self._windows[index].model_copy(deep=True)
        raise KeyError(f"window '{window.id}' not found")

    def delete_window(self, window_id: uuid.UUID) -> bool:
        for index, current in enumerate(self._windows):
            if current.id == window_id:
                del self._windows[index]
                return True
        return False
