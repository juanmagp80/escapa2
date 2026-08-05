"""Tests for the availability API endpoints and service."""

from __future__ import annotations

import uuid

from app.providers.mock_availability_provider import MockAvailabilityProvider
from app.services.availability_service import AvailabilityCreate, AvailabilityService
from fastapi.testclient import TestClient

WINDOW_ID = "10000000-0000-4000-8000-000000000001"
UNKNOWN_ID = "90000000-0000-4000-8000-000000000009"


def _payload() -> dict:
    return {
        "start_at": "2026-10-16T18:00:00+02:00",
        "end_at": "2026-10-18T22:00:00+02:00",
        "kind": "WEEKEND",
        "is_flexible": True,
    }


def test_list_availability_returns_seed(client: TestClient) -> None:
    response = client.get("/api/v1/availability")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    kinds = {item["kind"] for item in body}
    assert kinds == {"WEEKEND", "VACATION"}


def test_create_availability(client: TestClient) -> None:
    response = client.post("/api/v1/availability", json=_payload())
    assert response.status_code == 201
    body = response.json()
    uuid.UUID(body["id"])
    assert body["kind"] == "WEEKEND"
    assert body["is_flexible"] is True


def test_create_availability_invalid_range_is_rejected(client: TestClient) -> None:
    payload = _payload()
    payload["end_at"] = "2026-10-16T17:00:00+02:00"
    response = client.post("/api/v1/availability", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_put_availability_updates_window(client: TestClient) -> None:
    payload = {
        "start_at": "2026-11-06T18:00:00+02:00",
        "end_at": "2026-11-08T22:00:00+02:00",
        "kind": "VACATION",
        "is_flexible": False,
    }
    response = client.put(f"/api/v1/availability/{WINDOW_ID}", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == WINDOW_ID
    assert body["kind"] == "VACATION"
    assert body["is_flexible"] is False


def test_put_availability_unknown_returns_404(client: TestClient) -> None:
    response = client.put(f"/api/v1/availability/{UNKNOWN_ID}", json=_payload())
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_delete_availability(client: TestClient) -> None:
    created = client.post("/api/v1/availability", json=_payload()).json()
    response = client.delete(f"/api/v1/availability/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""
    remaining = client.get("/api/v1/availability").json()
    assert created["id"] not in {item["id"] for item in remaining}


def test_delete_availability_unknown_returns_404(client: TestClient) -> None:
    response = client.delete(f"/api/v1/availability/{UNKNOWN_ID}")
    assert response.status_code == 404


def test_invalid_window_id_returns_validation_error(client: TestClient) -> None:
    response = client.put("/api/v1/availability/not-a-uuid", json=_payload())
    assert response.status_code == 422


def test_service_create_and_get_roundtrip() -> None:
    service = AvailabilityService(MockAvailabilityProvider())
    created = service.create(
        AvailabilityCreate.model_validate(
            {
                "start_at": "2026-12-11T18:00:00+02:00",
                "end_at": "2026-12-13T22:00:00+02:00",
                "kind": "WEEKEND",
                "is_flexible": True,
            }
        )
    )
    fetched = service.get(created.id)
    assert fetched.id == created.id
    assert fetched.is_flexible is True


def test_service_delete_removes_window() -> None:
    service = AvailabilityService(MockAvailabilityProvider())
    first = service.list()[0]
    service.delete(first.id)
    assert first.id not in [window.id for window in service.list()]
