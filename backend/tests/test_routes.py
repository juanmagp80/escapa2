"""Tests for car route providers and fuel-station recommendation logic."""

from __future__ import annotations

import math
from datetime import UTC, datetime

from app.domain.fuel_stations import NearbyStation, recommend_fuel_stations
from app.domain.offers import FuelStation, RouteRequest
from app.providers.mock_fuel_price_provider import MockFuelPriceProvider
from app.providers.mock_route_provider import MockRouteProvider


def _station(station_id: str, name: str, price: float, lat: float, lon: float) -> FuelStation:
    return FuelStation(
        station_id=station_id,
        name=name,
        brand=None,
        latitude=lat,
        longitude=lon,
        price_per_liter_eur=price,
        fuels_available=["DIESEL"],
        last_updated=datetime.now(UTC),
    )


def test_mock_route_provider_is_deterministic() -> None:
    provider = MockRouteProvider()
    a = provider.calculate(RouteRequest(origin="Madrid", destination="Santiago de Compostela"))
    b = provider.calculate(RouteRequest(origin="Madrid", destination="Santiago de Compostela"))
    assert a == b
    assert a.origin == "Madrid"
    assert a.destination == "Santiago de Compostela"
    assert a.fuel_cost_eur > 0
    assert a.toll_cost_eur > 0
    assert a.vehicle_wear_cost_eur > 0
    assert math.isclose(a.total_cost_eur, a.summed_components, rel_tol=1e-9)


def test_mock_route_provider_total_equals_components() -> None:
    offer = MockRouteProvider().calculate(RouteRequest(origin="Madrid", destination="Porto"))
    assert offer.total_cost_eur == round(offer.summed_components, 2)


def test_mock_route_provider_unknown_pair_uses_default_distance() -> None:
    offer = MockRouteProvider().calculate(RouteRequest(origin="Lisboa", destination="Roma"))
    assert offer.distance_km == 550.0


def test_mock_fuel_price_provider_returns_two_stations() -> None:
    stations = MockFuelPriceProvider().stations_near_route(
        RouteRequest(origin="Madrid", destination="Santiago")
    )
    assert len(stations) == 2
    assert {station.station_id for station in stations} == {"ES001", "ES002"}
    assert all(station.price_per_liter_eur > 0 for station in stations)


def test_recommend_fuel_stations_ranks_by_net_savings_desc() -> None:
    cheap = _station("C", "Barata", 1.30, 40.41, -3.70)
    expensive = _station("E", "Cara", 1.60, 40.42, -3.71)
    nearby = [
        NearbyStation(station=expensive, detour_distance_km=10.0, detour_minutes=15.0),
        NearbyStation(station=cheap, detour_distance_km=10.0, detour_minutes=15.0),
    ]
    recommendations = recommend_fuel_stations(
        nearby,
        liters_to_refuel=30.0,
        reference_price_per_liter=1.60,
        consumption_l_per_100km=6.0,
        value_per_hour_eur=12.0,
    )
    assert recommendations[0].station.station_id == "C"
    assert recommendations[1].station.station_id == "E"
    assert recommendations[0].savings.net_savings_eur > recommendations[1].savings.net_savings_eur
    assert recommendations[0].worth_it is True


def test_recommend_fuel_stations_marks_losing_station_not_worth_it() -> None:
    station = _station("S", "Central", 1.595, 40.41, -3.70)
    nearby = [NearbyStation(station=station, detour_distance_km=40.0, detour_minutes=45.0)]
    recommendations = recommend_fuel_stations(
        nearby,
        liters_to_refuel=20.0,
        reference_price_per_liter=1.60,
        consumption_l_per_100km=8.0,
        value_per_hour_eur=15.0,
    )
    assert recommendations[0].worth_it is False
    assert recommendations[0].savings.net_savings_eur < 0
