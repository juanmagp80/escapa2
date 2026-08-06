"""SQLAlchemy repository for push device tokens."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy import CursorResult, delete, select
from sqlalchemy.orm import Session

from app.domain.notification import DeviceRegistration
from app.models.notification_device import NotificationDevice
from app.repositories._util import as_utc


class SqlDeviceRepository:
    """Device token registry backed by the database."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def list_tokens(self, user_id: str) -> list[str]:
        with self._session_factory() as session:
            rows = (
                session.execute(
                    select(NotificationDevice).where(NotificationDevice.user_id == user_id)
                )
                .scalars()
                .all()
            )
            return [row.token for row in rows]

    def register(self, device: DeviceRegistration) -> DeviceRegistration:
        with self._session_factory() as session:
            row = (
                session.execute(
                    select(NotificationDevice).where(NotificationDevice.token == device.token)
                )
                .scalars()
                .first()
            )
            now = datetime.now(UTC).replace(microsecond=0)
            if row is None:
                session.add(
                    NotificationDevice(
                        id=device.id,
                        user_id=device.user_id,
                        token=device.token,
                        platform=device.platform,
                        created_at=now,
                        updated_at=now,
                    )
                )
                session.commit()
                return device.model_copy(update={"created_at": now, "updated_at": now})
            row.user_id = device.user_id
            row.platform = device.platform
            row.updated_at = now
            session.commit()
            return DeviceRegistration(
                id=row.id,
                user_id=row.user_id,
                token=row.token,
                platform=row.platform,
                created_at=as_utc(row.created_at),
                updated_at=as_utc(row.updated_at),
            )

    def unregister(self, user_id: str, token: str) -> bool:
        with self._session_factory() as session:
            result = cast(
                CursorResult[Any],
                session.execute(
                    delete(NotificationDevice).where(
                        NotificationDevice.user_id == user_id,
                        NotificationDevice.token == token,
                    )
                ),
            )
            session.commit()
            return result.rowcount > 0
