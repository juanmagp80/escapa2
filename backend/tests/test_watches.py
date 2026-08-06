"""Tests for the search watches API endpoints and service."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from app.domain.opportunity import Opportunity, PriceSnapshot
from app.providers.mock_opportunity_provider import MockOpportunityProvider
from app.providers.mock_search_watch_provider import MockSearchWatchProvider
from app.services.search_watch_service import SearchWatchCreate, SearchWatchService
from fastapi.testclient import TestClient

WATCH_ID = "20000000-0000-4000-8000-000000000001"
UNKNOWN_ID = "90000000-0000-4000-8000-000000000009"


class SingleDroppingOpportunityProvider:
    """One opportunity whose current total may differ from its history."""

    def __init__(self, *, current_total: float) -> None:
        self._current_total = current_total
        self._snapshots: list[PriceSnapshot] = [
            PriceSnapshot(
                id=uuid.UUID("aaaaaaa0-aaaa-4aaa-8aaa-aaaaaaaaaaa1"),
                travel_opportunity_id=uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
                total_cost_eur=250.0,
                captured_at=datetime.now(UTC) - timedelta(days=1),
            )
        ]

    def list_opportunities(self) -> list[Opportunity]:
        return [self._opportunity()]

    def get_opportunity(self, opportunity_id: uuid.UUID) -> Opportunity | None:
        return self._opportunity() if opportunity_id == self._opportunity_id else None

    def price_history(self, opportunity_id: uuid.UUID) -> list[PriceSnapshot]:
        return list(self._snapshots)

    def save_snapshots(self, snapshots: list[PriceSnapshot]) -> None:
        self._snapshots.extend(snapshots)

    @property
    def _opportunity_id(self) -> uuid.UUID:
        return uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")

    def _opportunity(self) -> Opportunity:
        return Opportunity(
            id=self._opportunity_id,
            destination_code="OPO",
            destination_name="Porto",
            transport_mode="FLIGHT",
            start_at=datetime(2026, 8, 21, 8, 10, tzinfo=UTC),
            end_at=datetime(2026, 8, 23, 19, 30, tzinfo=UTC),
            useful_hours=40.0,
            total_cost_eur=self._current_total,
            cost_per_person_eur=self._current_total / 2,
            cost_per_night_eur=self._current_total / 2,
            cost_per_useful_hour_eur=self._current_total / 40.0,
            provider_verified_at=datetime.now(UTC),
        )


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
    matches = body["matched_opportunities"]
    assert len(matches) >= 1
    assert all(item["transport_mode"] == "FLIGHT" for item in matches)
    assert all(item["total_cost_eur"] <= 400 for item in matches)
    assert "last_run_at" in body
    assert "next_run_at" in body
    assert isinstance(body["alerts"], list)

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
    assert len(results.matched_opportunities) == len(MockOpportunityProvider().list_opportunities())
    assert after.last_run_at != before
    assert after.next_run_at is not None


def test_service_run_records_price_snapshots() -> None:
    opportunities = MockOpportunityProvider()
    service = SearchWatchService(MockSearchWatchProvider(), opportunities)
    watch = service.list_watches()[0]
    opportunity_id = opportunities.list_opportunities()[0].id

    before = len(opportunities.price_history(opportunity_id))
    service.run(watch.id)
    after = len(opportunities.price_history(opportunity_id))

    assert after == before + 1
    latest = opportunities.price_history(opportunity_id)[-1]
    assert latest.source_summary_json.get("watch_id") == str(watch.id)


def test_service_run_reports_triggered_alert_on_drop() -> None:
    provider = SingleDroppingOpportunityProvider(current_total=200.0)
    service = SearchWatchService(MockSearchWatchProvider(), provider)
    watch = service.create(
        SearchWatchCreate.model_validate(
            {
                "name": "Porto alerta",
                "criteria": {
                    "max_total_cost_eur": 400,
                    "initial_price_eur": 250.0,
                },
                "alert_rules": {"rules": ["Bajada superior a 4%", "Nuevo mínimo histórico"]},
            }
        )
    )

    result = service.run(watch.id)

    rules = {alert.rule for alert in result.alerts}
    assert "percent_drop" in rules
    assert "new_low" in rules
    assert any("Nuevo mínimo" in (alert.message or "") for alert in result.alerts)


def test_service_run_no_alert_without_change() -> None:
    provider = SingleDroppingOpportunityProvider(current_total=250.0)
    service = SearchWatchService(MockSearchWatchProvider(), provider)
    watch = service.create(
        SearchWatchCreate.model_validate(
            {
                "name": "Sin alerta",
                "criteria": {"max_total_cost_eur": 400, "initial_price_eur": 250.0},
                "alert_rules": {"rules": ["Bajada superior a 10%"]},
            }
        )
    )

    result = service.run(watch.id)

    assert result.alerts == []
