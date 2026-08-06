"""Tests for the search watches API endpoints and service."""

from __future__ import annotations

import uuid

from app.providers.mock_opportunity_provider import MockOpportunityProvider
from app.providers.mock_search_watch_provider import MockSearchWatchProvider
from app.services.search_watch_service import SearchWatchCreate, SearchWatchService
from fastapi.testclient import TestClient

WATCH_ID = "20000000-0000-4000-8000-000000000001"
UNKNOWN_ID = "90000000-0000-4000-8000-000000000009"


def _payload() -> dict:
    return {
        "name": "Roma en avión",
        "status": "ACTIVE",
        "criteria": {"max_total_cost_eur": 400, "transport_mode": "FLIGHT"},
        "alert_rules": {"rules": ["Nuevo mínimo histórico"]},
    }


def test_list_watches_returns_seed(client: TestClient) -> None:
    response = client.get("/api/v1/watches")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    names = {item["name"] for item in body}
    assert names == {"Porto en avión", "Galicia en coche"}


def test_create_watch(client: TestClient) -> None:
    response = client.post("/api/v1/watches", json=_payload())
    assert response.status_code == 201
    body = response.json()
    uuid.UUID(body["id"])
    assert body["name"] == "Roma en avión"
    assert body["status"] == "ACTIVE"
    assert body["criteria_json"] == {"max_total_cost_eur": 400, "transport_mode": "FLIGHT"}
    assert body["alert_rules_json"] == {"rules": ["Nuevo mínimo histórico"]}


def test_create_watch_empty_name_is_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/watches", json={"name": ""})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_get_watch(client: TestClient) -> None:
    response = client.get(f"/api/v1/watches/{WATCH_ID}")
    assert response.status_code == 200
    assert response.json()["name"] == "Porto en avión"


def test_get_watch_unknown_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/watches/{UNKNOWN_ID}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_put_watch_updates_fields(client: TestClient) -> None:
    response = client.put(
        f"/api/v1/watches/{WATCH_ID}",
        json={"name": "Porto revisado", "status": "PAUSED"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == WATCH_ID
    assert body["name"] == "Porto revisado"
    assert body["status"] == "PAUSED"


def test_put_watch_unknown_returns_404(client: TestClient) -> None:
    response = client.put(f"/api/v1/watches/{UNKNOWN_ID}", json={"name": "X"})
    assert response.status_code == 404


def test_delete_watch(client: TestClient) -> None:
    created = client.post("/api/v1/watches", json=_payload()).json()
    response = client.delete(f"/api/v1/watches/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""
    remaining = client.get("/api/v1/watches").json()
    assert created["id"] not in {item["id"] for item in remaining}


def test_delete_watch_unknown_returns_404(client: TestClient) -> None:
    response = client.delete(f"/api/v1/watches/{UNKNOWN_ID}")
    assert response.status_code == 404


def test_run_watch_returns_matching_opportunities(client: TestClient) -> None:
    created = client.post("/api/v1/watches", json=_payload()).json()
    response = client.post(f"/api/v1/watches/{created['id']}/run")
    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 1
    assert all(item["transport_mode"] == "FLIGHT" for item in body)
    assert all(item["total_cost_eur"] <= 400 for item in body)

    fetched = client.get(f"/api/v1/watches/{created['id']}").json()
    assert fetched["last_run_at"] is not None
    assert fetched["next_run_at"] is not None


def test_run_watch_unknown_returns_404(client: TestClient) -> None:
    response = client.post(f"/api/v1/watches/{UNKNOWN_ID}/run")
    assert response.status_code == 404


def test_invalid_watch_id_returns_validation_error(client: TestClient) -> None:
    response = client.get("/api/v1/watches/not-a-uuid")
    assert response.status_code == 422


def test_service_create_and_get_roundtrip() -> None:
    service = SearchWatchService(MockSearchWatchProvider(), MockOpportunityProvider())
    created = service.create(
        SearchWatchCreate.model_validate(
            {"name": "Venecia", "criteria": {"max_total_cost_eur": 300}}
        )
    )
    fetched = service.get(created.id)
    assert fetched.id == created.id
    assert fetched.name == "Venecia"
    assert fetched.criteria_json == {"max_total_cost_eur": 300}


def test_service_run_refreshes_timestamps() -> None:
    service = SearchWatchService(MockSearchWatchProvider(), MockOpportunityProvider())
    watch = service.list_watches()[0]
    before = watch.last_run_at
    results = service.run(watch.id)
    after = service.get(watch.id)
    assert len(results) == len(MockOpportunityProvider().list_opportunities())
    assert after.last_run_at != before
    assert after.next_run_at is not None
