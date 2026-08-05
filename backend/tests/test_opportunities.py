"""Tests for the opportunities API endpoints."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

SANTIAGO_ID = "11111111-1111-4111-8111-111111111111"
SEVILLA_ID = "22222222-2222-4222-8222-222222222222"
PORTO_ID = "33333333-3333-4333-8333-333333333333"
PORTO_CHEAP_ID = "44444444-4444-4444-8444-444444444444"
UNKNOWN_ID = "99999999-9999-4999-8999-999999999999"


def test_list_opportunities_returns_four(client: TestClient) -> None:
    response = client.get("/api/v1/opportunities")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 4
    names = {item["destination_name"] for item in body}
    assert "Santiago de Compostela" in names
    assert "Porto" in names


def test_opportunity_exposes_cost_metrics(client: TestClient) -> None:
    response = client.get(f"/api/v1/opportunities/{PORTO_ID}")
    assert response.status_code == 200
    item = response.json()
    assert item["destination_name"] == "Porto"
    assert item["total_cost_eur"] == 312.0
    assert item["cost_per_person_eur"] == 156.0
    assert item["cost_per_night_eur"] == 156.0
    assert item["cost_per_useful_hour_eur"] == 7.8
    assert item["useful_hours"] == 40.0


def test_cheaper_opportunity_has_fewer_useful_hours(client: TestClient) -> None:
    response = client.get(f"/api/v1/opportunities/{PORTO_CHEAP_ID}")
    item = response.json()
    assert item["total_cost_eur"] == 214.0
    assert item["useful_hours"] == 12.0
    assert item["cost_per_useful_hour_eur"] == 17.83


def test_filter_by_max_total_cost(client: TestClient) -> None:
    response = client.get("/api/v1/opportunities", params={"max_total_cost_eur": 250})
    assert response.status_code == 200
    items = response.json()
    assert all(item["total_cost_eur"] <= 250.0 for item in items)
    assert len(items) == 3


def test_filter_by_transport_mode(client: TestClient) -> None:
    response = client.get("/api/v1/opportunities", params={"transport_mode": "FLIGHT"})
    assert response.status_code == 200
    items = response.json()
    assert items and all(item["transport_mode"] == "FLIGHT" for item in items)


def test_filter_by_min_useful_hours(client: TestClient) -> None:
    response = client.get("/api/v1/opportunities", params={"min_useful_hours": 20})
    items = response.json()
    assert all(item["useful_hours"] >= 20.0 for item in items)
    assert len(items) == 3


def test_filter_by_destination(client: TestClient) -> None:
    response = client.get("/api/v1/opportunities", params={"destination": "porto"})
    items = response.json()
    assert all("porto" in item["destination_name"].lower() for item in items)
    assert len(items) == 2


def test_sort_by_total_cost_ascending(client: TestClient) -> None:
    response = client.get("/api/v1/opportunities", params={"sort": "total_cost_eur"})
    items = response.json()
    totals = [item["total_cost_eur"] for item in items]
    assert totals == sorted(totals)


def test_sort_by_total_cost_descending(client: TestClient) -> None:
    response = client.get("/api/v1/opportunities", params={"sort": "-total_cost_eur"})
    items = response.json()
    totals = [item["total_cost_eur"] for item in items]
    assert totals == sorted(totals, reverse=True)


def test_invalid_sort_returns_validation_error(client: TestClient) -> None:
    response = client.get("/api/v1/opportunities", params={"sort": "bogus_field"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_get_unknown_opportunity_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/opportunities/{UNKNOWN_ID}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_price_history_returns_snapshots(client: TestClient) -> None:
    response = client.get(f"/api/v1/opportunities/{SANTIAGO_ID}/price-history")
    assert response.status_code == 200
    snapshots = response.json()
    assert len(snapshots) == 2
    first, second = snapshots
    assert first["total_cost_eur"] == 212.0
    assert second["total_cost_eur"] == 198.0


def test_price_history_unknown_opportunity_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/opportunities/{UNKNOWN_ID}/price-history")
    assert response.status_code == 404


def test_invalid_opportunity_id_returns_validation_error(client: TestClient) -> None:
    response = client.get("/api/v1/opportunities/not-a-uuid")
    assert response.status_code == 422


def test_mock_ids_are_valid_uuids(client: TestClient) -> None:
    response = client.get("/api/v1/opportunities")
    for item in response.json():
        uuid.UUID(item["id"])
