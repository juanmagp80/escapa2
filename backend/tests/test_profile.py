"""Tests for the profile API endpoints and service."""

from __future__ import annotations

import uuid

from app.providers.mock_profile_provider import MockProfileProvider
from app.services.profile_service import (
    AirportPreferenceInput,
    ProfileService,
    ProfileUpdate,
    VehicleInput,
)
from fastapi.testclient import TestClient

PROFILE_ID = "00000000-0000-4000-8000-000000000001"


def test_get_profile_returns_default(client: TestClient) -> None:
    response = client.get("/api/v1/profile")
    assert response.status_code == 200
    body = response.json()
    assert body["origin_city"] == "Madrid"
    assert body["currency"] == "EUR"
    assert body["default_budget_eur"] == 350.0
    assert body["preferred_transport"] == "EITHER"


def test_put_profile_updates_mutable_fields(client: TestClient) -> None:
    payload = {
        "origin_city": "Barcelona",
        "currency": "eur",
        "default_budget_eur": 500.0,
        "max_drive_minutes": 300,
        "preferred_transport": "CAR",
        "interests": [" playa ", "", "montaña"],
        "avoid_preferences": [],
    }
    response = client.put("/api/v1/profile", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["origin_city"] == "Barcelona"
    assert body["currency"] == "EUR"
    assert body["default_budget_eur"] == 500.0
    assert body["max_drive_minutes"] == 300
    assert body["preferred_transport"] == "CAR"
    assert body["interests"] == ["playa", "montaña"]
    assert body["id"] == PROFILE_ID


def test_put_profile_validation_error(client: TestClient) -> None:
    payload = {"origin_city": ""}
    response = client.put("/api/v1/profile", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_put_profile_negative_budget_is_rejected(client: TestClient) -> None:
    payload = {
        "origin_city": "Madrid",
        "currency": "EUR",
        "default_budget_eur": -10.0,
    }
    response = client.put("/api/v1/profile", json=payload)
    assert response.status_code == 422


def test_get_airports_returns_preferences(client: TestClient) -> None:
    response = client.get("/api/v1/profile/airports")
    assert response.status_code == 200
    airports = response.json()
    assert len(airports) == 2
    codes = {airport["iata_code"] for airport in airports}
    assert codes == {"MAD", "BCN"}


def test_put_airports_replaces_list(client: TestClient) -> None:
    payload = [
        {"iata_code": "agp", "enabled": True, "transfer_cost_eur": 25.0, "transfer_minutes": 20},
        {"iata_code": "SVQ", "enabled": True},
    ]
    response = client.put("/api/v1/profile/airports", json=payload)
    assert response.status_code == 200
    airports = response.json()
    assert len(airports) == 2
    codes = {airport["iata_code"] for airport in airports}
    assert codes == {"AGP", "SVQ"}
    assert all(uuid.UUID(airport["id"]) for airport in airports)
    assert all(airport["travel_profile_id"] == PROFILE_ID for airport in airports)


def test_put_airports_invalid_iata_is_rejected(client: TestClient) -> None:
    response = client.put("/api/v1/profile/airports", json=[{"iata_code": "XX"}])
    assert response.status_code == 422


def test_service_preserves_immutable_fields() -> None:
    service = ProfileService(MockProfileProvider())
    original = service.get()
    updated = service.update(
        ProfileUpdate(
            origin_city="Valencia",
            currency="EUR",
            default_budget_eur=400.0,
            max_drive_minutes=None,
            preferred_transport="EITHER",
            interests=["ciudad"],
            avoid_preferences=[],
        )
    )
    assert updated.id == original.id
    assert updated.created_at == original.created_at
    assert updated.updated_at >= original.updated_at


def test_service_replaces_airports() -> None:
    service = ProfileService(MockProfileProvider())
    inputs = [
        AirportPreferenceInput(iata_code="MAD", enabled=True),
        AirportPreferenceInput(iata_code="BCN", enabled=False),
    ]
    result = service.replace_airports(inputs)
    assert [airport.iata_code for airport in result] == ["MAD", "BCN"]
    stored = service.get_airports()
    assert len(stored) == 2
    assert all(airport.id is not None for airport in stored)


def test_get_vehicle_returns_default(client: TestClient) -> None:
    response = client.get("/api/v1/profile/vehicle")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Coche habitual"
    assert body["fuel_type"] == "DIESEL"
    assert body["average_consumption_l_per_100km"] == 6.0
    assert body["tank_capacity_l"] == 55.0
    assert body["travel_profile_id"] == PROFILE_ID


def test_put_vehicle_updates_mutable_fields(client: TestClient) -> None:
    payload = {
        "name": "Furgoneta",
        "fuel_type": "GASOLINE",
        "average_consumption_l_per_100km": 8.5,
        "tank_capacity_l": 60.0,
        "estimated_cost_per_km_eur": 0.14,
        "max_fuel_detour_minutes": 20,
    }
    response = client.put("/api/v1/profile/vehicle", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Furgoneta"
    assert body["fuel_type"] == "GASOLINE"
    assert body["average_consumption_l_per_100km"] == 8.5
    assert body["max_fuel_detour_minutes"] == 20


def test_put_vehicle_electric_allows_missing_consumption(client: TestClient) -> None:
    payload = {
        "name": "Coche eléctrico",
        "fuel_type": "ELECTRIC",
        "estimated_cost_per_km_eur": 0.05,
    }
    response = client.put("/api/v1/profile/vehicle", json=payload)
    assert response.status_code == 200
    assert response.json()["fuel_type"] == "ELECTRIC"
    assert response.json()["average_consumption_l_per_100km"] is None


def test_put_vehicle_requires_consumption_for_fuel_vehicles(client: TestClient) -> None:
    payload = {
        "name": "Coche",
        "fuel_type": "DIESEL",
    }
    response = client.put("/api/v1/profile/vehicle", json=payload)
    assert response.status_code == 422


def test_put_vehicle_unknown_fuel_type_is_rejected(client: TestClient) -> None:
    payload = {
        "name": "Coche",
        "fuel_type": "GAS",
    }
    response = client.put("/api/v1/profile/vehicle", json=payload)
    assert response.status_code == 422


def test_service_preserves_vehicle_identity() -> None:
    service = ProfileService(MockProfileProvider())
    original = service.get_vehicle()
    updated = service.save_vehicle(
        VehicleInput(
            name="Nuevo",
            fuel_type="DIESEL",
            average_consumption_l_per_100km=7.0,
        )
    )
    assert updated.id == original.id
    assert updated.travel_profile_id == original.travel_profile_id
    assert updated.updated_at >= original.updated_at
