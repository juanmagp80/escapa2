"""SQLAlchemy repository for the notification log."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import NotificationStatus, NotificationType
from app.domain.notification import NotificationLog
from app.models.notification_log import NotificationLogORM
from app.repositories._util import as_utc


class SqlNotificationLogRepository:
    """Notification log backed by the database."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def add(self, log: NotificationLog) -> NotificationLog:
        with self._session_factory() as session:
            session.add(
                NotificationLogORM(
                    id=log.id,
                    user_id=log.user_id,
                    search_watch_id=log.search_watch_id,
                    type=log.type.value,
                    title=log.title,
                    body=log.body,
                    payload_json=log.payload_json,
                    sent_at=log.sent_at,
                    status=log.status.value,
                )
            )
            session.commit()
            return log

    def list_for_user(self, user_id: str) -> list[NotificationLog]:
        with self._session_factory() as session:
            rows = (
                session.execute(
                    select(NotificationLogORM)
                    .where(NotificationLogORM.user_id == user_id)
                    .order_by(NotificationLogORM.sent_at.desc())
                    .limit(50)
                )
                .scalars()
                .all()
            )
            return [self._to_domain(row) for row in rows]

    @staticmethod
    def _to_domain(row: NotificationLogORM) -> NotificationLog:
        return NotificationLog(
            id=row.id,
            user_id=row.user_id,
            search_watch_id=row.search_watch_id,
            type=NotificationType(row.type),
            title=row.title,
            body=row.body,
            payload_json=dict(row.payload_json),
            sent_at=as_utc(row.sent_at) or datetime.now(UTC),
            status=NotificationStatus(row.status),
        )
