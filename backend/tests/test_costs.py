"""Tests for pure cost and useful-hours calculation rules."""

from __future__ import annotations

import math
from datetime import UTC, datetime

from app.domain.costs import (
    CostComponents,
    UsefulHoursBreakdown,
    cost_per_night,
    cost_per_person,
    cost_per_useful_hour,
    estimate_fuel_cost,
    estimate_vehicle_wear,
    route_cost_components,
    total_trip_cost,
)
from app.domain.offers import RouteOffer


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


def test_estimate_fuel_cost() -> None:
    cost = estimate_fuel_cost(distance_km=550.0, consumption_l_per_100km=6.0, price_per_liter=1.6)
    assert math.isclose(cost, 52.8)


def test_estimate_fuel_cost_invalid_inputs_is_none() -> None:
    assert estimate_fuel_cost(-1.0, 6.0, 1.6) is None
    assert estimate_fuel_cost(550.0, -1.0, 1.6) is None
    assert estimate_fuel_cost(550.0, 6.0, -1.0) is None


def test_estimate_vehicle_wear() -> None:
    assert math.isclose(estimate_vehicle_wear(550.0, 0.10), 55.0)


def test_estimate_vehicle_wear_unknown_cost_is_none() -> None:
    assert estimate_vehicle_wear(550.0, None) is None


def test_route_cost_components_maps_breakdown() -> None:
    offer = RouteOffer(
        provider_offer_id="route-1",
        origin="Madrid",
        destination="Santiago",
        distance_km=540.0,
        duration_minutes=405.0,
        fuel_cost_eur=51.84,
        toll_cost_eur=30.78,
        parking_cost_eur=23.76,
        vehicle_wear_cost_eur=27.0,
        total_cost_eur=133.38,
        route_polyline="poly",
        verified_at=datetime.now(UTC),
    )
    components = route_cost_components(offer)
    assert components.route_fuel_total == 51.84
    assert components.toll_total == 30.78
    assert components.destination_parking_total == 23.76
    assert components.vehicle_wear_total == 27.0
    assert total_trip_cost(components) == 133.38
