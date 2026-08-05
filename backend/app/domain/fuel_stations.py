"""Pure fuel-station net-savings calculation rules.

A station is recommended by net savings, not just by its price per liter. The
detour fuel cost and a time penalty are subtracted from the gross savings
(AGENTS.md 9.4).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FuelStationNetSavings:
    """Explainable result of refueling at a station on the route."""

    gross_savings_eur: float
    detour_fuel_cost_eur: float
    time_penalty_eur: float
    net_savings_eur: float


def liters_to_refuel(
    tank_capacity_l: float,
    current_fuel_l: float,
) -> float | None:
    """Liters the couple can refuel, or None when inputs are invalid."""
    if tank_capacity_l <= 0 or current_fuel_l < 0:
        return None
    return max(0.0, tank_capacity_l - current_fuel_l)


def gross_savings(
    liters: float,
    reference_price_per_liter: float,
    station_price_per_liter: float,
) -> float:
    """Money saved by refueling at the station price instead of the reference."""
    return liters * (reference_price_per_liter - station_price_per_liter)


def detour_fuel_cost(
    detour_distance_km: float,
    consumption_l_per_100km: float,
    station_price_per_liter: float,
) -> float:
    """Fuel cost of the detour needed to reach the station."""
    return detour_distance_km * consumption_l_per_100km / 100 * station_price_per_liter


def time_penalty(
    detour_minutes: float,
    value_per_hour_eur: float,
) -> float:
    """Monetary value of the time spent on the detour."""
    return detour_minutes / 60 * value_per_hour_eur


def net_savings(
    *,
    liters_to_refuel: float,
    reference_price_per_liter: float,
    station_price_per_liter: float,
    detour_distance_km: float,
    consumption_l_per_100km: float,
    detour_minutes: float,
    value_per_hour_eur: float,
) -> FuelStationNetSavings:
    """Return the explainable net savings of refueling at a station."""
    gross = gross_savings(
        liters_to_refuel,
        reference_price_per_liter,
        station_price_per_liter,
    )
    detour_cost = detour_fuel_cost(
        detour_distance_km,
        consumption_l_per_100km,
        station_price_per_liter,
    )
    penalty = time_penalty(detour_minutes, value_per_hour_eur)
    return FuelStationNetSavings(
        gross_savings_eur=round(gross, 2),
        detour_fuel_cost_eur=round(detour_cost, 2),
        time_penalty_eur=round(penalty, 2),
        net_savings_eur=round(gross - detour_cost - penalty, 2),
    )
