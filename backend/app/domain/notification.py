"""Normalized domain models for push notifications.

Notifications are always derived from confirmed price events (alerts evaluated
against real snapshots); the payload only carries non-sensitive data.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import NotificationStatus, NotificationType


class NotificationLog(BaseModel):
    """A record of an attempt to notify a user about a watched trip."""

    id: uuid.UUID
    user_id: str = Field(..., max_length=120)
    search_watch_id: uuid.UUID | None = None
    type: NotificationType
    title: str = Field(..., max_length=200)
    body: str = Field(..., max_length=500)
    payload_json: dict[str, object] = Field(default_factory=dict)
    sent_at: datetime
    status: NotificationStatus


class DeviceRegistration(BaseModel):
    """A push token registered by a device for a user."""

    id: uuid.UUID
    user_id: str = Field(..., max_length=120)
    token: str = Field(..., min_length=10, max_length=500)
    platform: str = Field(default="android", max_length=30)
    created_at: datetime
    updated_at: datetime


__all__ = ["DeviceRegistration", "NotificationLog"]
