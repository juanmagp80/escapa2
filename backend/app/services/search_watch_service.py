"""Search watch application service.

Applies business rules on top of the watch provider: input validation,
existence checks and a simulated run that refreshes the schedule and returns
the opportunities that match the stored criteria.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field

from app.core.errors import NotFoundError
from app.domain.enums import TransportMode, WatchStatus
from app.domain.opportunity import Opportunity
from app.domain.search_watch import SearchWatch
from app.providers.opportunity_provider import OpportunityProvider
from app.providers.search_watch_provider import SearchWatchProvider

DEV_COUPLE_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
RUN_INTERVAL = timedelta(days=1)


class SearchWatchCreate(BaseModel):
    """Fields accepted by POST /watches."""

    name: str = Field(..., min_length=1, max_length=120)
    status: WatchStatus = WatchStatus.ACTIVE
    criteria: dict[str, object] = Field(default_factory=dict)
    alert_rules: dict[str, object] = Field(default_factory=dict)


class SearchWatchUpdate(BaseModel):
    """Fields accepted by PUT /watches/{id}."""

    name: str | None = Field(default=None, min_length=1, max_length=120)
    status: WatchStatus | None = None
    criteria: dict[str, object] | None = None
    alert_rules: dict[str, object] | None = None


class SearchWatchService:
    """Application service exposing search watch operations."""

    def __init__(
        self,
        watch_provider: SearchWatchProvider,
        opportunity_provider: OpportunityProvider,
    ) -> None:
        self._watches = watch_provider
        self._opportunities = opportunity_provider

    def list_watches(self) -> list[SearchWatch]:
        return self._watches.list_watches()

    def get(self, watch_id: uuid.UUID) -> SearchWatch:
        watch = self._watches.get_watch(watch_id)
        if watch is None:
            raise NotFoundError("search watch", str(watch_id))
        return watch

    def create(self, data: SearchWatchCreate) -> SearchWatch:
        now = datetime.now(UTC)
        watch = SearchWatch(
            id=uuid.uuid4(),
            couple_id=DEV_COUPLE_ID,
            name=data.name,
            status=data.status,
            criteria_json=dict(data.criteria),
            alert_rules_json=dict(data.alert_rules),
            next_run_at=now + RUN_INTERVAL,
            created_at=now,
            updated_at=now,
        )
        return self._watches.create_watch(watch)

    def update(self, watch_id: uuid.UUID, data: SearchWatchUpdate) -> SearchWatch:
        current = self.get(watch_id)
        changes: dict[str, object] = {}
        if data.name is not None:
            changes["name"] = data.name
        if data.status is not None:
            changes["status"] = data.status
        if data.criteria is not None:
            changes["criteria_json"] = dict(data.criteria)
        if data.alert_rules is not None:
            changes["alert_rules_json"] = dict(data.alert_rules)
        changes["updated_at"] = datetime.now(UTC)
        updated = current.model_copy(update=changes)
        return self._watches.update_watch(updated)

    def delete(self, watch_id: uuid.UUID) -> None:
        if not self._watches.delete_watch(watch_id):
            raise NotFoundError("search watch", str(watch_id))

    def run(self, watch_id: uuid.UUID) -> list[Opportunity]:
        """Simulate a scheduled run.

        Refreshes the run timestamps and returns the opportunities that match
        the stored criteria (budget and transport), so the Radar can later
        evaluate alerts over a real provider without changing the contract.
        """
        watch = self.get(watch_id)
        now = datetime.now(UTC)
        refreshed = watch.model_copy(
            update={
                "last_run_at": now,
                "next_run_at": now + RUN_INTERVAL,
                "updated_at": now,
            }
        )
        self._watches.update_watch(refreshed)

        criteria = watch.criteria_json
        max_total = criteria.get("max_total_cost_eur")
        transport = criteria.get("transport_mode")

        opportunities = self._opportunities.list_opportunities()
        if isinstance(max_total, (int, float)):
            opportunities = [
                item
                for item in opportunities
                if item.total_cost_eur is not None and item.total_cost_eur <= float(max_total)
            ]
        if isinstance(transport, str):
            try:
                expected = TransportMode(transport)
            except ValueError:
                expected = None
            if expected is not None:
                opportunities = [item for item in opportunities if item.transport_mode == expected]
        return opportunities
