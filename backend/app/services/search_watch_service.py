"""Search watch application service.

Applies business rules on top of the watch provider: input validation,
existence checks and a run that refreshes the schedule, records price
snapshots and evaluates the configured alert rules over the matching
opportunities.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field

from app.core.errors import NotFoundError
from app.domain.alerts import (
    AlertConfig,
    AlertEvaluation,
    evaluate_price_alerts,
    parse_alert_rules,
)
from app.domain.enums import TransportMode, WatchStatus
from app.domain.opportunity import Opportunity, PriceSnapshot
from app.domain.search_watch import ALERT_RULES_KEY, CRITERIA_INITIAL_PRICE_KEY, SearchWatch
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


class WatchRunAlert(BaseModel):
    """A single alert result reported by a watch run."""

    rule: str
    message: str | None = None


class WatchRunResult(BaseModel):
    """Result of running a watch: schedule, matches and triggered alerts."""

    last_run_at: datetime | None
    next_run_at: datetime | None
    matched_opportunities: list[Opportunity] = Field(default_factory=list)
    alerts: list[WatchRunAlert] = Field(default_factory=list)


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

    def run(self, watch_id: uuid.UUID) -> WatchRunResult:
        """Execute a watch run.

        Refreshes the run schedule, records a price snapshot for each matching
        opportunity and evaluates the configured alert rules against the
        recorded price history.
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
        opportunities = self._match_opportunities(criteria)

        alerts: list[WatchRunAlert] = []
        raw_rules = watch.alert_rules_json.get(ALERT_RULES_KEY, [])
        config = (
            parse_alert_rules([str(rule) for rule in raw_rules])
            if isinstance(raw_rules, list)
            else AlertConfig()
        )

        snapshots: list[PriceSnapshot] = []
        for opportunity in opportunities:
            snapshot = self._record_snapshot(watch, opportunity, now)
            if snapshot is not None:
                snapshots.append(snapshot)
            alerts.extend(
                self._evaluate_watch_alerts(
                    opportunity,
                    criteria,
                    config,
                )
            )

        if snapshots:
            self._opportunities.save_snapshots(snapshots)

        return WatchRunResult(
            last_run_at=refreshed.last_run_at,
            next_run_at=refreshed.next_run_at,
            matched_opportunities=opportunities,
            alerts=alerts,
        )

    def _match_opportunities(self, criteria: dict[str, object]) -> list[Opportunity]:
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

    def _record_snapshot(
        self,
        watch: SearchWatch,
        opportunity: Opportunity,
        captured_at: datetime,
    ) -> PriceSnapshot | None:
        if opportunity.total_cost_eur is None:
            return None
        return PriceSnapshot(
            id=uuid.uuid4(),
            travel_opportunity_id=opportunity.id,
            total_cost_eur=opportunity.total_cost_eur,
            flight_cost_eur=opportunity.flight_cost_eur,
            hotel_cost_eur=opportunity.hotel_cost_eur,
            route_cost_eur=opportunity.route_cost_eur,
            captured_at=captured_at,
            source_summary_json={"provider": "watch-run", "watch_id": str(watch.id)},
        )

    def _evaluate_watch_alerts(
        self,
        opportunity: Opportunity,
        criteria: dict[str, object],
        config: AlertConfig,
    ) -> list[WatchRunAlert]:
        history = self._opportunities.price_history(opportunity.id)
        previous = _latest_total(history)
        if previous is None:
            initial = criteria.get(CRITERIA_INITIAL_PRICE_KEY)
            if isinstance(initial, (int, float)):
                previous = float(initial)
        min_recorded = _min_recorded(history)
        if min_recorded is None:
            initial = criteria.get(CRITERIA_INITIAL_PRICE_KEY)
            if isinstance(initial, (int, float)):
                min_recorded = float(initial)

        budget = criteria.get("budget_eur")
        if not isinstance(budget, (int, float)):
            budget = None

        evaluations: list[AlertEvaluation] = evaluate_price_alerts(
            current_total_eur=opportunity.total_cost_eur,
            previous_total_eur=previous,
            min_recorded_eur=min_recorded if config.new_low else None,
            budget_eur=float(budget) if config.budget_match and budget is not None else None,
            below_threshold_eur=config.below_threshold_eur,
            percent_drop_threshold=config.percent_drop_threshold,
            absolute_drop_threshold_eur=config.absolute_drop_threshold_eur,
            consecutive_rises=0,
            rises_to_alert=0,
        )
        return [
            WatchRunAlert(rule=evaluation.rule, message=evaluation.message)
            for evaluation in evaluations
            if evaluation.triggered
        ]


def _latest_total(history: list[PriceSnapshot]) -> float | None:
    totals = [
        snapshot.total_cost_eur for snapshot in history if snapshot.total_cost_eur is not None
    ]
    return totals[-1] if totals else None


def _min_recorded(history: list[PriceSnapshot]) -> float | None:
    totals = [
        snapshot.total_cost_eur for snapshot in history if snapshot.total_cost_eur is not None
    ]
    return min(totals) if totals else None
