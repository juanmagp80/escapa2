"""SQLAlchemy repository for availability windows.

Implements the ``AvailabilityProvider`` protocol on top of the ORM model.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.availability import AvailabilityWindow
from app.domain.enums import WindowKind
from app.models.availability_window import AvailabilityWindow as AvailabilityWindowORM
from app.repositories._util import as_utc


class SqlAvailabilityRepository:
    """Availability provider backed by the database."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def list_windows(self) -> list[AvailabilityWindow]:
        with self._session_factory() as session:
            rows = (
                session.execute(
                    select(AvailabilityWindowORM).order_by(AvailabilityWindowORM.start_at)
                )
                .scalars()
                .all()
            )
            return [self._to_domain(row) for row in rows]

    def get_window(self, window_id: uuid.UUID) -> AvailabilityWindow | None:
        with self._session_factory() as session:
            row = session.get(AvailabilityWindowORM, window_id)
            return self._to_domain(row) if row is not None else None

    def create_window(self, window: AvailabilityWindow) -> AvailabilityWindow:
        with self._session_factory() as session:
            row = AvailabilityWindowORM(
                id=window.id,
                start_at=window.start_at,
                end_at=window.end_at,
                kind=window.kind.value,
                is_flexible=window.is_flexible,
                created_at=window.created_at or datetime.now(UTC),
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def update_window(self, window: AvailabilityWindow) -> AvailabilityWindow:
        with self._session_factory() as session:
            row = session.get(AvailabilityWindowORM, window.id)
            if row is None:
                return window
            row.start_at = window.start_at
            row.end_at = window.end_at
            row.kind = window.kind.value
            row.is_flexible = window.is_flexible
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def delete_window(self, window_id: uuid.UUID) -> bool:
        with self._session_factory() as session:
            row = session.get(AvailabilityWindowORM, window_id)
            if row is None:
                return False
            session.delete(row)
            session.commit()
            return True

    @staticmethod
    def _to_domain(row: AvailabilityWindowORM) -> AvailabilityWindow:
        return AvailabilityWindow(
            id=row.id,
            start_at=as_utc(row.start_at),
            end_at=as_utc(row.end_at),
            kind=WindowKind(row.kind),
            is_flexible=row.is_flexible,
            created_at=as_utc(row.created_at),
        )
