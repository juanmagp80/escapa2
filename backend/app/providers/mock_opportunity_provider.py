"""In-memory provider with simulated opportunities for development and tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.domain.costs import (
    CostComponents,
    UsefulHoursBreakdown,
    cost_per_night,
    cost_per_person,
    cost_per_useful_hour,
    total_trip_cost,
)
from app.domain.enums import TransportMode
from app.domain.opportunity import Opportunity, PriceSnapshot
from app.domain.scoring import (
    ValueScoreBreakdown,
    budget_fit_score,
    relative_price_score,
    schedule_fit_score,
    useful_time_score,
)
from app.domain.scoring import (
    comfort_score as comfort_component,
)


def _utc(iso: str) -> datetime:
    return datetime.fromisoformat(iso).astimezone(UTC)


_DEFAULT_BUDGET_EUR = 350.0
_MATCHES_WEEKEND = {
    uuid.UUID("11111111-1111-4111-8111-111111111111"): True,
    uuid.UUID("22222222-2222-4222-8222-222222222222"): True,
    uuid.UUID("33333333-3333-4333-8333-333333333333"): True,
    uuid.UUID("44444444-4444-4444-8444-444444444444"): True,
}
_WITHIN_VACATION = {
    uuid.UUID("11111111-1111-4111-8111-111111111111"): True,
    uuid.UUID("22222222-2222-4222-8222-222222222222"): True,
    uuid.UUID("33333333-3333-4333-8333-333333333333"): True,
    uuid.UUID("44444444-4444-4444-8444-444444444444"): True,
}
_DIRECT_TRANSPORT = {
    uuid.UUID("11111111-1111-4111-8111-111111111111"): True,
    uuid.UUID("22222222-2222-4222-8222-222222222222"): True,
    uuid.UUID("33333333-3333-4333-8333-333333333333"): True,
    uuid.UUID("44444444-4444-4444-8444-444444444444"): True,
}
_FREE_CANCELLATION = {
    uuid.UUID("11111111-1111-4111-8111-111111111111"): True,
    uuid.UUID("22222222-2222-4222-8222-222222222222"): True,
    uuid.UUID("33333333-3333-4333-8333-333333333333"): True,
    uuid.UUID("44444444-4444-4444-8444-444444444444"): False,
}
_PARKING_AVAILABLE = {
    uuid.UUID("11111111-1111-4111-8111-111111111111"): True,
    uuid.UUID("22222222-2222-4222-8222-222222222222"): True,
    uuid.UUID("33333333-3333-4333-8333-333333333333"): False,
    uuid.UUID("44444444-4444-4444-8444-444444444444"): False,
}


def _build_opportunity(
    *,
    opportunity_id: str,
    destination_code: str,
    destination_name: str,
    transport_mode: TransportMode,
    start_at: str,
    end_at: str,
    breakdown: UsefulHoursBreakdown,
    components: CostComponents,
    travelers: int,
    nights: int,
    verified_at: str,
) -> Opportunity:
    total = total_trip_cost(components)
    useful_hours = breakdown.useful_hours
    per_person = cost_per_person(total, travelers)
    per_night = cost_per_night(total, nights)
    per_useful_hour = cost_per_useful_hour(total, useful_hours)
    return Opportunity(
        id=uuid.UUID(opportunity_id),
        destination_code=destination_code,
        destination_name=destination_name,
        transport_mode=transport_mode,
        start_at=_utc(start_at),
        end_at=_utc(end_at),
        useful_hours=round(useful_hours, 1),
        total_cost_eur=round(total, 2),
        cost_per_person_eur=round(per_person, 2) if per_person is not None else None,
        cost_per_night_eur=round(per_night, 2) if per_night is not None else None,
        cost_per_useful_hour_eur=(
            round(per_useful_hour, 2) if per_useful_hour is not None else None
        ),
        provider_verified_at=_utc(verified_at),
    )


def _apply_value_scores(opportunities: list[Opportunity]) -> list[Opportunity]:
    """Compute explainable value scores from the reference price range.

    The range of observed totals is used as the reference for the relative
    price component, so the cheapest option scores the highest there.
    """
    totals = [item.total_cost_eur for item in opportunities if item.total_cost_eur is not None]
    if not totals:
        return opportunities
    reference_min = min(totals)
    reference_max = max(totals)
    scored: list[Opportunity] = []
    for item in opportunities:
        total = item.total_cost_eur
        budget_fit = budget_fit_score(total, _DEFAULT_BUDGET_EUR) if total else None
        relative = relative_price_score(total, reference_min, reference_max) if total else None
        value = ValueScoreBreakdown(
            budget_fit_score=budget_fit if budget_fit is not None else 0.0,
            relative_price_score=relative if relative is not None else 0.0,
            useful_time_score=(
                useful_time_score(item.useful_hours) if item.useful_hours is not None else None
            )
            or 0.0,
            schedule_fit_score=schedule_fit_score(
                _MATCHES_WEEKEND.get(item.id, False),
                _WITHIN_VACATION.get(item.id, False),
            ),
            comfort_score=comfort_component(
                _DIRECT_TRANSPORT.get(item.id, False),
                _FREE_CANCELLATION.get(item.id, False),
                _PARKING_AVAILABLE.get(item.id, False),
            ),
        )
        scored.append(item.model_copy(update={"value_score": value.value_score}))
    return scored


class MockOpportunityProvider:
    """Serves the four reference opportunities described in AGENTS.md.

    Demonstrates total cost, cost per person, per night and per useful hour,
    plus a price difference between the current value and an older snapshot.
    """

    def __init__(self) -> None:
        self._opportunities: list[Opportunity] = [
            _build_opportunity(
                opportunity_id="11111111-1111-4111-8111-111111111111",
                destination_code="GAL",
                destination_name="Santiago de Compostela",
                transport_mode=TransportMode.CAR,
                start_at="2026-08-14T18:30:00+02:00",
                end_at="2026-08-16T20:00:00+02:00",
                breakdown=UsefulHoursBreakdown(
                    window_hours=48.0,
                    transit_to_destination_hours=1.0,
                    airport_wait_hours=0.0,
                    transport_hours=8.0,
                    accommodation_transfer_hours=0.5,
                    return_margin_hours=2.0,
                    transit_back_hours=2.5,
                ),
                components=CostComponents(
                    route_fuel_total=90.0,
                    toll_total=32.0,
                    destination_parking_total=24.0,
                    hotel_total=52.0,
                ),
                travelers=2,
                nights=2,
                verified_at="2026-08-05T12:00:00+00:00",
            ),
            _build_opportunity(
                opportunity_id="22222222-2222-4222-8222-222222222222",
                destination_code="SVQ",
                destination_name="Sevilla",
                transport_mode=TransportMode.FLIGHT,
                start_at="2026-08-14T19:45:00+02:00",
                end_at="2026-08-16T21:10:00+02:00",
                breakdown=UsefulHoursBreakdown(
                    window_hours=43.0,
                    transit_to_destination_hours=1.0,
                    airport_wait_hours=2.0,
                    transport_hours=4.0,
                    accommodation_transfer_hours=1.0,
                    return_margin_hours=2.0,
                    transit_back_hours=3.0,
                ),
                components=CostComponents(
                    flight_total=170.0,
                    airport_transfer_total=28.0,
                    hotel_total=48.0,
                ),
                travelers=2,
                nights=2,
                verified_at="2026-08-05T12:00:00+00:00",
            ),
            _build_opportunity(
                opportunity_id="33333333-3333-4333-8333-333333333333",
                destination_code="OPO",
                destination_name="Porto",
                transport_mode=TransportMode.FLIGHT,
                start_at="2026-08-21T08:10:00+02:00",
                end_at="2026-08-23T19:30:00+02:00",
                breakdown=UsefulHoursBreakdown(
                    window_hours=52.0,
                    transit_to_destination_hours=1.0,
                    airport_wait_hours=2.0,
                    transport_hours=3.0,
                    accommodation_transfer_hours=1.0,
                    return_margin_hours=2.0,
                    transit_back_hours=3.0,
                ),
                components=CostComponents(
                    flight_total=210.0,
                    airport_transfer_total=30.0,
                    hotel_total=72.0,
                ),
                travelers=2,
                nights=2,
                verified_at="2026-08-05T12:00:00+00:00",
            ),
            _build_opportunity(
                opportunity_id="44444444-4444-4444-8444-444444444444",
                destination_code="OPO",
                destination_name="Porto (horario ajustado)",
                transport_mode=TransportMode.FLIGHT,
                start_at="2026-08-21T22:00:00+02:00",
                end_at="2026-08-23T06:30:00+02:00",
                breakdown=UsefulHoursBreakdown(
                    window_hours=25.0,
                    transit_to_destination_hours=1.0,
                    airport_wait_hours=2.5,
                    transport_hours=3.0,
                    accommodation_transfer_hours=1.0,
                    return_margin_hours=3.0,
                    transit_back_hours=2.5,
                ),
                components=CostComponents(
                    flight_total=150.0,
                    airport_transfer_total=30.0,
                    hotel_total=34.0,
                ),
                travelers=2,
                nights=2,
                verified_at="2026-08-05T12:00:00+00:00",
            ),
        ]
        self._opportunities = _apply_value_scores(
            [
                _build_opportunity(
                    opportunity_id="11111111-1111-4111-8111-111111111111",
                    destination_code="GAL",
                    destination_name="Santiago de Compostela",
                    transport_mode=TransportMode.CAR,
                    start_at="2026-08-14T18:30:00+02:00",
                    end_at="2026-08-16T20:00:00+02:00",
                    breakdown=UsefulHoursBreakdown(
                        window_hours=48.0,
                        transit_to_destination_hours=1.0,
                        airport_wait_hours=0.0,
                        transport_hours=8.0,
                        accommodation_transfer_hours=0.5,
                        return_margin_hours=2.0,
                        transit_back_hours=2.5,
                    ),
                    components=CostComponents(
                        route_fuel_total=90.0,
                        toll_total=32.0,
                        destination_parking_total=24.0,
                        hotel_total=52.0,
                    ),
                    travelers=2,
                    nights=2,
                    verified_at="2026-08-05T12:00:00+00:00",
                ),
                _build_opportunity(
                    opportunity_id="22222222-2222-4222-8222-222222222222",
                    destination_code="SVQ",
                    destination_name="Sevilla",
                    transport_mode=TransportMode.FLIGHT,
                    start_at="2026-08-14T19:45:00+02:00",
                    end_at="2026-08-16T21:10:00+02:00",
                    breakdown=UsefulHoursBreakdown(
                        window_hours=43.0,
                        transit_to_destination_hours=1.0,
                        airport_wait_hours=2.0,
                        transport_hours=4.0,
                        accommodation_transfer_hours=1.0,
                        return_margin_hours=2.0,
                        transit_back_hours=3.0,
                    ),
                    components=CostComponents(
                        flight_total=170.0,
                        airport_transfer_total=28.0,
                        hotel_total=48.0,
                    ),
                    travelers=2,
                    nights=2,
                    verified_at="2026-08-05T12:00:00+00:00",
                ),
                _build_opportunity(
                    opportunity_id="33333333-3333-4333-8333-333333333333",
                    destination_code="OPO",
                    destination_name="Porto",
                    transport_mode=TransportMode.FLIGHT,
                    start_at="2026-08-21T08:10:00+02:00",
                    end_at="2026-08-23T19:30:00+02:00",
                    breakdown=UsefulHoursBreakdown(
                        window_hours=52.0,
                        transit_to_destination_hours=1.0,
                        airport_wait_hours=2.0,
                        transport_hours=3.0,
                        accommodation_transfer_hours=1.0,
                        return_margin_hours=2.0,
                        transit_back_hours=3.0,
                    ),
                    components=CostComponents(
                        flight_total=210.0,
                        airport_transfer_total=30.0,
                        hotel_total=72.0,
                    ),
                    travelers=2,
                    nights=2,
                    verified_at="2026-08-05T12:00:00+00:00",
                ),
                _build_opportunity(
                    opportunity_id="44444444-4444-4444-8444-444444444444",
                    destination_code="OPO",
                    destination_name="Porto (horario ajustado)",
                    transport_mode=TransportMode.FLIGHT,
                    start_at="2026-08-21T22:00:00+02:00",
                    end_at="2026-08-23T06:30:00+02:00",
                    breakdown=UsefulHoursBreakdown(
                        window_hours=25.0,
                        transit_to_destination_hours=1.0,
                        airport_wait_hours=2.5,
                        transport_hours=3.0,
                        accommodation_transfer_hours=1.0,
                        return_margin_hours=3.0,
                        transit_back_hours=2.5,
                    ),
                    components=CostComponents(
                        flight_total=150.0,
                        airport_transfer_total=30.0,
                        hotel_total=34.0,
                    ),
                    travelers=2,
                    nights=2,
                    verified_at="2026-08-05T12:00:00+00:00",
                ),
            ]
        )
        self._snapshots: list[PriceSnapshot] = [
            PriceSnapshot(
                id=uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
                travel_opportunity_id=uuid.UUID("11111111-1111-4111-8111-111111111111"),
                total_cost_eur=212.0,
                route_cost_eur=122.0,
                hotel_cost_eur=52.0,
                captured_at=_utc("2026-08-02T12:00:00+00:00"),
                source_summary_json={"provider": "mock", "currency": "EUR"},
            ),
            PriceSnapshot(
                id=uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
                travel_opportunity_id=uuid.UUID("11111111-1111-4111-8111-111111111111"),
                total_cost_eur=198.0,
                route_cost_eur=122.0,
                hotel_cost_eur=52.0,
                captured_at=_utc("2026-08-05T12:00:00+00:00"),
                source_summary_json={"provider": "mock", "currency": "EUR"},
            ),
            PriceSnapshot(
                id=uuid.UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc"),
                travel_opportunity_id=uuid.UUID("33333333-3333-4333-8333-333333333333"),
                total_cost_eur=328.0,
                flight_cost_eur=226.0,
                hotel_cost_eur=72.0,
                captured_at=_utc("2026-08-02T12:00:00+00:00"),
                source_summary_json={"provider": "mock", "currency": "EUR"},
            ),
            PriceSnapshot(
                id=uuid.UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
                travel_opportunity_id=uuid.UUID("33333333-3333-4333-8333-333333333333"),
                total_cost_eur=312.0,
                flight_cost_eur=210.0,
                hotel_cost_eur=72.0,
                captured_at=_utc("2026-08-05T12:00:00+00:00"),
                source_summary_json={"provider": "mock", "currency": "EUR"},
            ),
        ]

    def list_opportunities(self) -> list[Opportunity]:
        return list(self._opportunities)

    def get_opportunity(self, opportunity_id: uuid.UUID) -> Opportunity | None:
        return next(
            (item for item in self._opportunities if item.id == opportunity_id),
            None,
        )

    def price_history(self, opportunity_id: uuid.UUID) -> list[PriceSnapshot]:
        return [
            snapshot
            for snapshot in self._snapshots
            if snapshot.travel_opportunity_id == opportunity_id
        ]
