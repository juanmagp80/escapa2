"""Shared domain enums."""

from __future__ import annotations

from enum import StrEnum


class TransportMode(StrEnum):
    FLIGHT = "FLIGHT"
    CAR = "CAR"
    EITHER = "EITHER"


class Confidence(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class WindowKind(StrEnum):
    WEEKEND = "WEEKEND"
    VACATION = "VACATION"


class WatchStatus(StrEnum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"


class NotificationType(StrEnum):
    NEW_LOW = "NEW_LOW"
    PRICE_DROP = "PRICE_DROP"
    BUDGET_MATCH = "BUDGET_MATCH"
    NEW_OPPORTUNITY = "NEW_OPPORTUNITY"
    PRICE_RISING = "PRICE_RISING"
    DAILY_REPORT = "DAILY_REPORT"


class NotificationStatus(StrEnum):
    SENT = "SENT"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class FuelType(StrEnum):
    DIESEL = "DIESEL"
    GASOLINE = "GASOLINE"
    HYBRID = "HYBRID"
    ELECTRIC = "ELECTRIC"
