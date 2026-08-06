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
