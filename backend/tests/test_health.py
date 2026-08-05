"""Tests for system health endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"]


def test_ready_degraded_when_database_unavailable(client: TestClient, monkeypatch) -> None:
    class BrokenEngine:
        def connect(self) -> None:
            raise RuntimeError("database down")

    monkeypatch.setattr("app.api.v1.health.engine", BrokenEngine())
    response = client.get("/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"] == {"database": "down"}


def test_ready_ok_when_database_available(client: TestClient, monkeypatch) -> None:
    class FakeConnection:
        def execute(self, _: object) -> None:
            return None

        def __enter__(self) -> FakeConnection:
            return self

        def __exit__(self, *_: object) -> bool:
            return False

    class FakeEngine:
        def connect(self) -> FakeConnection:
            return FakeConnection()

    monkeypatch.setattr("app.api.v1.health.engine", FakeEngine())
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
