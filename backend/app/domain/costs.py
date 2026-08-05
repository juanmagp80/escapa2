"""Pure trip cost and useful-hours calculation rules.

All calculations live here as pure functions so they can be unit-tested in
isolation and reused by services, schedulers and alert rules.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostComponents:
    """Applicable cost components of a trip.

    Components that do not apply default to zero and are excluded from the sum
    when the caller builds the instance.
    """

    flight_total: float = 0.0
    airport_transfer_total: float = 0.0
    airport_parking_total: float = 0.0
    hotel_total: float = 0.0
    destination_transport_total: float = 0.0
    route_fuel_total: float = 0.0
    toll_total: float = 0.0
    destination_parking_total: float = 0.0
    vehicle_wear_total: float = 0.0
    known_taxes_and_fees: float = 0.0


def total_trip_cost(components: CostComponents) -> float:
    """Total trip cost for two travelers using the applicable components."""
    return (
        components.flight_total
        + components.airport_transfer_total
        + components.airport_parking_total
        + components.hotel_total
        + components.destination_transport_total
        + components.route_fuel_total
        + components.toll_total
        + components.destination_parking_total
        + components.vehicle_wear_total
        + components.known_taxes_and_fees
    )


def cost_per_person(total_cost_eur: float, travelers: int) -> float | None:
    """Return cost per traveler, or None when not calculable."""
    if travelers <= 0:
        return None
    return total_cost_eur / travelers


def cost_per_night(total_cost_eur: float, nights: int) -> float | None:
    """Return cost per night, or None when not calculable."""
    if nights <= 0:
        return None
    return total_cost_eur / nights


def cost_per_useful_hour(total_cost_eur: float, useful_hours: float) -> float | None:
    """Return cost per useful hour, or None when not calculable."""
    if useful_hours <= 0:
        return None
    return total_cost_eur / useful_hours


@dataclass(frozen=True)
class UsefulHoursBreakdown:
    """Explainable breakdown of time spent around the trip.

    Useful hours represent the time actually available in the destination after
    discounting transit, waits, transfers and the safety margin before return.
    """

    window_hours: float
    transit_to_destination_hours: float
    airport_wait_hours: float
    transport_hours: float
    accommodation_transfer_hours: float
    return_margin_hours: float
    transit_back_hours: float

    @property
    def useful_hours(self) -> float:
        """Total useful hours in destination."""
        return max(
            0.0,
            self.window_hours
            - self.transit_to_destination_hours
            - self.airport_wait_hours
            - self.transport_hours
            - self.accommodation_transfer_hours
            - self.return_margin_hours
            - self.transit_back_hours,
        )
