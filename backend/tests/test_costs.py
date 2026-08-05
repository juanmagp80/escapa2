"""Tests for pure cost and useful-hours calculation rules."""

from __future__ import annotations

import math

from app.domain.costs import (
    CostComponents,
    UsefulHoursBreakdown,
    cost_per_night,
    cost_per_person,
    cost_per_useful_hour,
    total_trip_cost,
)


def test_total_trip_cost_sums_applicable_components() -> None:
    components = CostComponents(
        flight_total=170.0,
        airport_transfer_total=28.0,
        hotel_total=48.0,
    )
    assert total_trip_cost(components) == 246.0


def test_total_trip_cost_without_components_is_zero() -> None:
    assert total_trip_cost(CostComponents()) == 0.0


def test_cost_per_person() -> None:
    assert cost_per_person(246.0, 2) == 123.0


def test_cost_per_person_invalid_travelers_is_none() -> None:
    assert cost_per_person(246.0, 0) is None


def test_cost_per_night() -> None:
    assert cost_per_night(246.0, 2) == 123.0


def test_cost_per_night_invalid_nights_is_none() -> None:
    assert cost_per_night(246.0, 0) is None


def test_cost_per_useful_hour() -> None:
    assert math.isclose(cost_per_useful_hour(312.0, 40.0), 7.8)


def test_cost_per_useful_hour_invalid_hours_is_none() -> None:
    assert cost_per_useful_hour(312.0, 0.0) is None


def test_useful_hours_subtracts_time_sinks() -> None:
    breakdown = UsefulHoursBreakdown(
        window_hours=52.0,
        transit_to_destination_hours=1.0,
        airport_wait_hours=2.0,
        transport_hours=3.0,
        accommodation_transfer_hours=1.0,
        return_margin_hours=2.0,
        transit_back_hours=3.0,
    )
    assert breakdown.useful_hours == 40.0


def test_useful_hours_never_negative() -> None:
    breakdown = UsefulHoursBreakdown(
        window_hours=5.0,
        transit_to_destination_hours=2.0,
        airport_wait_hours=2.0,
        transport_hours=2.0,
        accommodation_transfer_hours=1.0,
        return_margin_hours=2.0,
        transit_back_hours=2.0,
    )
    assert breakdown.useful_hours == 0.0
