"""Tests for the fuel-station net-savings calculation rules."""

from __future__ import annotations

import math

from app.domain.fuel_stations import (
    detour_fuel_cost,
    gross_savings,
    liters_to_refuel,
    net_savings,
    time_penalty,
)


def test_liters_to_refuel() -> None:
    assert liters_to_refuel(50.0, 20.0) == 30.0


def test_liters_to_refuel_full_tank_is_zero() -> None:
    assert liters_to_refuel(50.0, 50.0) == 0.0


def test_liters_to_refuel_invalid_inputs_is_none() -> None:
    assert liters_to_refuel(0.0, 10.0) is None
    assert liters_to_refuel(50.0, -5.0) is None


def test_gross_savings() -> None:
    assert math.isclose(gross_savings(30.0, 1.60, 1.30), 9.0)


def test_detour_fuel_cost() -> None:
    cost = detour_fuel_cost(10.0, 6.0, 1.30)
    assert math.isclose(cost, 0.78)


def test_time_penalty() -> None:
    assert time_penalty(30.0, 12.0) == 6.0


def test_net_savings_positive_when_station_is_worth_it() -> None:
    result = net_savings(
        liters_to_refuel=30.0,
        reference_price_per_liter=1.60,
        station_price_per_liter=1.30,
        detour_distance_km=10.0,
        consumption_l_per_100km=6.0,
        detour_minutes=15.0,
        value_per_hour_eur=12.0,
    )
    assert math.isclose(result.gross_savings_eur, 9.0)
    assert math.isclose(result.detour_fuel_cost_eur, 0.78)
    assert math.isclose(result.time_penalty_eur, 3.0)
    assert math.isclose(result.net_savings_eur, 5.22)


def test_net_savings_negative_when_detour_is_not_worth_it() -> None:
    result = net_savings(
        liters_to_refuel=20.0,
        reference_price_per_liter=1.60,
        station_price_per_liter=1.58,
        detour_distance_km=40.0,
        consumption_l_per_100km=8.0,
        detour_minutes=45.0,
        value_per_hour_eur=15.0,
    )
    assert result.net_savings_eur < 0.0
