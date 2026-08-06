"""Normalized domain models for watched trip searches."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import WatchStatus

COUPLE_JSON_KEY = "couple_id"
CRITERIA_INITIAL_PRICE_KEY = "initial_price_eur"
ALERT_RULES_KEY = "rules"


class SearchWatch(BaseModel):
    """A recurring search the couple wants to keep an eye on."""

    id: uuid.UUID
    couple_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=120)
    status: WatchStatus = WatchStatus.ACTIVE
    criteria_json: dict[str, object] = Field(default_factory=dict)
    alert_rules_json: dict[str, object] = Field(default_factory=dict)
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
