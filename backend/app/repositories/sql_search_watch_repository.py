"""SQLAlchemy repository for search watches.

Implements the ``SearchWatchProvider`` protocol on top of the ORM model.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import WatchStatus
from app.domain.search_watch import SearchWatch
from app.models.search_watch import SearchWatch as SearchWatchORM
from app.repositories._util import as_utc


class SqlSearchWatchRepository:
    """Search watch provider backed by the database."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def list_watches(self) -> list[SearchWatch]:
        with self._session_factory() as session:
            rows = (
                session.execute(select(SearchWatchORM).order_by(SearchWatchORM.created_at))
                .scalars()
                .all()
            )
            return [self._to_domain(row) for row in rows]

    def get_watch(self, watch_id: uuid.UUID) -> SearchWatch | None:
        with self._session_factory() as session:
            row = session.get(SearchWatchORM, watch_id)
            return self._to_domain(row) if row is not None else None

    def create_watch(self, watch: SearchWatch) -> SearchWatch:
        with self._session_factory() as session:
            row = SearchWatchORM(
                id=watch.id,
                name=watch.name,
                status=watch.status.value,
                criteria_json=dict(watch.criteria_json),
                alert_rules_json=dict(watch.alert_rules_json),
                last_run_at=watch.last_run_at,
                next_run_at=watch.next_run_at,
                created_at=watch.created_at or datetime.now(UTC),
                updated_at=watch.updated_at or datetime.now(UTC),
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def update_watch(self, watch: SearchWatch) -> SearchWatch:
        with self._session_factory() as session:
            row = session.get(SearchWatchORM, watch.id)
            if row is None:
                return watch
            row.name = watch.name
            row.status = watch.status.value
            row.criteria_json = dict(watch.criteria_json)
            row.alert_rules_json = dict(watch.alert_rules_json)
            row.last_run_at = watch.last_run_at
            row.next_run_at = watch.next_run_at
            row.updated_at = datetime.now(UTC)
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def delete_watch(self, watch_id: uuid.UUID) -> bool:
        with self._session_factory() as session:
            row = session.get(SearchWatchORM, watch_id)
            if row is None:
                return False
            session.delete(row)
            session.commit()
            return True

    @staticmethod
    def _to_domain(row: SearchWatchORM) -> SearchWatch:
        return SearchWatch(
            id=row.id,
            couple_id=row.couple_id,
            name=row.name,
            status=WatchStatus(row.status),
            criteria_json=dict(row.criteria_json or {}),
            alert_rules_json=dict(row.alert_rules_json or {}),
            last_run_at=as_utc(row.last_run_at) if row.last_run_at is not None else None,
            next_run_at=as_utc(row.next_run_at) if row.next_run_at is not None else None,
            created_at=as_utc(row.created_at),
            updated_at=as_utc(row.updated_at),
        )
