"""Tests for the AI endpoints, providers, rate limiting and cache."""

from __future__ import annotations

import pytest
from app.ai.cache import AiResponseCache, cache_key
from app.ai.fake import FakeAiProvider
from app.ai.gemini import GeminiAiProvider
from app.ai.rate_limit import AiRateLimiter
from app.ai.schemas import (
    DailyReportRequest,
    DailyReportResponse,
    InterpretSearchRequest,
    InterpretSearchResponse,
    OpportunitySummaryRequest,
    OpportunitySummaryResponse,
)
from app.api.deps import get_ai_provider
from app.core.config import Settings
from app.core.errors import ProviderUnavailableError, RateLimitedError
from app.main import app
from app.services.ai_service import AiService
from fastapi.testclient import TestClient


def _payload() -> dict:
    return {
        "destination": "Bologna",
        "travelers": 2,
        "total_cost_eur": 312.0,
        "budget_eur": 350.0,
        "useful_hours": 29.0,
        "transport_mode": "FLIGHT",
        "verified_at": "2026-08-05T12:00:00Z",
        "facts": [
            "Direct flight",
            "Two hotel nights",
            "Airport transfer not included",
        ],
    }


def _interpret_payload() -> dict:
    return {
        "query": (
            "Queremos salir desde Madrid con un presupuesto de 400 euros para dos, "
            "en coche, y nos gusta la playa."
        )
    }


def _itinerary_payload() -> dict:
    return {
        "destination": "Santiago de Compostela",
        "start_date": "2026-08-14",
        "end_date": "2026-08-16",
        "transport_mode": "CAR",
        "budget_eur": 350.0,
        "interests": ["gastronomía", "ciudad"],
        "facts": ["Hotel with free cancellation"],
    }


def _daily_report_payload() -> dict:
    return {
        "report_date": "2026-08-06",
        "watches": [
            {
                "watch_name": "Porto finde",
                "destination": "Porto",
                "current_total_eur": 312.0,
                "previous_total_eur": 328.0,
                "min_recorded_eur": 312.0,
                "budget_eur": 350.0,
                "facts": ["Direct flight"],
            },
            {
                "watch_name": "Sevilla puente",
                "destination": "Sevilla",
                "current_total_eur": 246.0,
                "previous_total_eur": 240.0,
                "budget_eur": 200.0,
            },
        ],
    }


def test_opportunity_summary_deterministic_within_budget(client: TestClient) -> None:
    response = client.post("/api/v1/ai/opportunity-summary", json=_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["generated_by_ai"] is False
    assert body["headline"] == "Buena opción dentro del presupuesto"
    assert "312.00" in body["summary"]
    assert any("38.00 EUR" in pro for pro in body["pros"])


def test_opportunity_summary_over_budget(client: TestClient) -> None:
    payload = _payload()
    payload["total_cost_eur"] = 400.0
    response = client.post("/api/v1/ai/opportunity-summary", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["headline"] == "Por encima del presupuesto"
    assert any("50.00 EUR" in con for con in body["cons"])


def test_opportunity_summary_validation_error(client: TestClient) -> None:
    response = client.post("/api/v1/ai/opportunity-summary", json={"destination": ""})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


class FailingProvider:
    async def summarize_opportunity(self, _: OpportunitySummaryRequest) -> None:
        raise ProviderUnavailableError()


def test_opportunity_summary_falls_back_when_ai_fails(client: TestClient) -> None:
    app.dependency_overrides[get_ai_provider] = lambda: FailingProvider()
    try:
        response = client.post("/api/v1/ai/opportunity-summary", json=_payload())
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["generated_by_ai"] is False
    assert body["headline"] == "Buena opción dentro del presupuesto"


@pytest.mark.asyncio
async def test_fake_provider_returns_valid_schema() -> None:
    provider = FakeAiProvider()
    request = OpportunitySummaryRequest.model_validate(_payload())
    result = await provider.summarize_opportunity(request)
    assert isinstance(result, OpportunitySummaryResponse)
    assert result.confidence.value == "MEDIUM"


def test_interpret_search_deterministic(client: TestClient) -> None:
    response = client.post("/api/v1/ai/interpret-search", json=_interpret_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["origin_city"] == "Madrid"
    assert body["budget_eur"] == 400.0
    assert body["travelers"] == 2
    assert body["preferred_transport"] == "CAR"
    assert "playa" in body["interests"]
    assert body["generated_by_ai"] is False


def test_interpret_search_validation_error(client: TestClient) -> None:
    response = client.post("/api/v1/ai/interpret-search", json={"query": ""})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_interpret_search_confidence_grows_with_data() -> None:
    provider = FakeAiProvider()
    low = await provider.interpret_search(InterpretSearchRequest(query="un finde relajado"))
    high = await provider.interpret_search(
        InterpretSearchRequest(query=_interpret_payload()["query"])
    )
    assert low.confidence.value == "LOW"
    assert high.confidence.value == "HIGH"


def test_itinerary_deterministic(client: TestClient) -> None:
    response = client.post("/api/v1/ai/itineraries", json=_itinerary_payload())
    assert response.status_code == 200
    body = response.json()
    assert len(body["days"]) == 3
    assert body["days"][0]["date"] == "2026-08-14"
    assert body["generated_by_ai"] is False
    assert any("orientativo" in warning for warning in body["warnings"])


def test_itinerary_rejects_inverted_range(client: TestClient) -> None:
    payload = _itinerary_payload()
    payload["start_date"], payload["end_date"] = payload["end_date"], payload["start_date"]
    response = client.post("/api/v1/ai/itineraries", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_daily_report_deterministic_reports_drop(client: TestClient) -> None:
    response = client.post("/api/v1/ai/daily-report", json=_daily_report_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["generated_by_ai"] is False
    assert "Porto" in body["headline"]
    entries = {entry["destination"]: entry for entry in body["entries"]}
    assert entries["Porto"]["change_eur"] == 16.0
    assert entries["Porto"]["is_new_low"] is True
    assert entries["Porto"]["within_budget"] is True
    assert entries["Sevilla"]["is_new_low"] is False
    assert entries["Sevilla"]["within_budget"] is False
    assert any("Nuevo mínimo" in entry["recommendation"] for entry in body["entries"])


def test_daily_report_empty_watches_after_clean_is_validation_error(
    client: TestClient,
) -> None:
    payload = {"report_date": "2026-08-06", "watches": [{"watch_name": "  ", "destination": "X"}]}
    response = client.post("/api/v1/ai/daily-report", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_daily_report_requires_at_least_one_watch(client: TestClient) -> None:
    response = client.post("/api/v1/ai/daily-report", json={"report_date": "2026-08-06"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_fake_daily_report_is_schema_valid() -> None:
    provider = FakeAiProvider()
    request = DailyReportRequest.model_validate(_daily_report_payload())
    result = await provider.generate_daily_report(request)
    assert isinstance(result, DailyReportResponse)
    assert len(result.entries) == 2
    assert all(entry.confidence.value == "HIGH" for entry in result.entries)


class DailyReportFailingProvider(GeminiAiProvider):
    def __init__(self) -> None:
        super().__init__(Settings(gemini_enabled=True, gemini_api_key="test-key"))

    async def generate_daily_report(self, _: DailyReportRequest) -> DailyReportResponse:
        raise ProviderUnavailableError()


@pytest.mark.asyncio
async def test_ai_service_daily_report_falls_back_when_external_fails() -> None:
    service = AiService(DailyReportFailingProvider(), model="gemini-3.6-flash")
    request = DailyReportRequest.model_validate(_daily_report_payload())
    result = await service.generate_daily_report(request, "user")
    assert result.generated_by_ai is False
    assert any("Nuevo mínimo" in entry.recommendation for entry in result.entries)


def test_rate_limiter_blocks_after_quota() -> None:
    limiter = AiRateLimiter(max_requests_per_day=2)
    limiter.check_and_consume("user")
    limiter.check_and_consume("user")
    with pytest.raises(RateLimitedError):
        limiter.check_and_consume("user")
    assert limiter.remaining("user") == 0
    limiter.check_and_consume("other")
    assert limiter.remaining("other") == 1


def test_rate_limiter_reset() -> None:
    limiter = AiRateLimiter(max_requests_per_day=1)
    limiter.check_and_consume("user")
    limiter.reset()
    limiter.check_and_consume("user")


def test_cache_hits_and_evicts() -> None:
    request = InterpretSearchRequest(query="buscar playa")
    cache: AiResponseCache[InterpretSearchResponse] = AiResponseCache("test-model", max_entries=2)
    first = InterpretSearchResponse(confidence="MEDIUM", generated_by_ai=False)
    second = InterpretSearchResponse(confidence="HIGH", generated_by_ai=False)
    assert cache.get(request) is None
    cache.set(request, first)
    assert cache.get(request) == first
    other = InterpretSearchRequest(query="otra búsqueda")
    cache.set(other, second)
    cache.set(InterpretSearchRequest(query="tercera"), second)
    assert len(cache) <= 2


def test_cache_key_is_stable_and_sensitive_to_input() -> None:
    a = InterpretSearchRequest(query="playa en agosto")
    b = InterpretSearchRequest(query="playa en agosto")
    c = InterpretSearchRequest(query="montaña en agosto")
    assert cache_key("m", a) == cache_key("m", b)
    assert cache_key("m", a) != cache_key("m", c)
    assert cache_key("m", a) != cache_key("n", a)


class CountingGeminiProvider(GeminiAiProvider):
    """External-looking provider that counts calls and can fail."""

    def __init__(self, *, fail: bool = False) -> None:
        super().__init__(Settings(gemini_enabled=True, gemini_api_key="test-key"))
        self.calls = 0
        self._fail = fail

    async def interpret_search(self, request: InterpretSearchRequest) -> InterpretSearchResponse:
        self.calls += 1
        if self._fail:
            raise ProviderUnavailableError()
        return InterpretSearchResponse(confidence="HIGH", generated_by_ai=True)


@pytest.mark.asyncio
async def test_ai_service_caches_external_results() -> None:
    provider = CountingGeminiProvider()
    service = AiService(provider, model="gemini-3.6-flash")
    request = InterpretSearchRequest(query="buscar playa")
    first = await service.interpret_search(request, "user")
    second = await service.interpret_search(request, "user")
    assert first.generated_by_ai is True
    assert provider.calls == 1
    assert second == first


@pytest.mark.asyncio
async def test_ai_service_falls_back_when_external_fails() -> None:
    provider = CountingGeminiProvider(fail=True)
    service = AiService(provider, model="gemini-3.6-flash")
    request = InterpretSearchRequest(query="buscar playa")
    result = await service.interpret_search(request, "user")
    assert result.generated_by_ai is False
    assert provider.calls == 1


@pytest.mark.asyncio
async def test_ai_service_rate_limits_external_calls() -> None:
    provider = CountingGeminiProvider()
    service = AiService(provider, max_requests_per_user_day=1, model="gemini-3.6-flash")
    first = InterpretSearchRequest(query="primera")
    second = InterpretSearchRequest(query="segunda")
    await service.interpret_search(first, "user")
    with pytest.raises(RateLimitedError):
        await service.interpret_search(second, "user")
