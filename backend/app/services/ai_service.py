"""AI application service combining provider, rate limiting and cache.

The service is the only place the API interacts with AI. It applies the per-user
daily quota, serves cached responses for repeated identical requests, and falls
back to deterministic rules when the external provider fails.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

from pydantic import BaseModel

from app.ai.cache import AiResponseCache
from app.ai.fake import (
    fallback_daily_report,
    fallback_interpretation,
    fallback_itinerary,
    fallback_summary,
)
from app.ai.gemini import GeminiAiProvider
from app.ai.protocol import AiProvider
from app.ai.rate_limit import AiRateLimiter
from app.ai.schemas import (
    DailyReportRequest,
    DailyReportResponse,
    InterpretSearchRequest,
    InterpretSearchResponse,
    ItineraryAiRequest,
    ItineraryAiResponse,
    OpportunitySummaryRequest,
    OpportunitySummaryResponse,
)
from app.core.errors import ProviderUnavailableError

ReqT = TypeVar("ReqT", bound=BaseModel)
ResT = TypeVar("ResT", bound=BaseModel)


class AiService:
    """Orchestrates AI calls with quota, cache and rule-based fallback."""

    def __init__(
        self,
        provider: AiProvider,
        *,
        max_requests_per_user_day: int = 20,
        model: str = "gemini",
    ) -> None:
        self._provider = provider
        self._rate_limiter = AiRateLimiter(max_requests_per_user_day)
        self._summary_cache: AiResponseCache[OpportunitySummaryResponse] = AiResponseCache(model)
        self._interpret_cache: AiResponseCache[InterpretSearchResponse] = AiResponseCache(model)
        self._itinerary_cache: AiResponseCache[ItineraryAiResponse] = AiResponseCache(model)
        self._daily_report_cache: AiResponseCache[DailyReportResponse] = AiResponseCache(model)
        self._external = isinstance(provider, GeminiAiProvider)

    @property
    def uses_external_ai(self) -> bool:
        """True when the backing provider performs external calls."""
        return self._external

    async def summarize_opportunity(
        self,
        request: OpportunitySummaryRequest,
        user_key: str,
    ) -> OpportunitySummaryResponse:
        return await self._call(
            user_key,
            request,
            self._summary_cache,
            self._provider.summarize_opportunity,
            fallback_summary,
        )

    async def interpret_search(
        self,
        request: InterpretSearchRequest,
        user_key: str,
    ) -> InterpretSearchResponse:
        return await self._call(
            user_key,
            request,
            self._interpret_cache,
            self._provider.interpret_search,
            fallback_interpretation,
        )

    async def generate_itinerary(
        self,
        request: ItineraryAiRequest,
        user_key: str,
    ) -> ItineraryAiResponse:
        return await self._call(
            user_key,
            request,
            self._itinerary_cache,
            self._provider.generate_itinerary,
            fallback_itinerary,
        )

    async def generate_daily_report(
        self,
        request: DailyReportRequest,
        user_key: str,
    ) -> DailyReportResponse:
        return await self._call(
            user_key,
            request,
            self._daily_report_cache,
            self._provider.generate_daily_report,
            fallback_daily_report,
        )

    async def _call(
        self,
        user_key: str,
        request: ReqT,
        cache: AiResponseCache[ResT],
        call: Callable[[ReqT], Awaitable[ResT]],
        fallback: Callable[[ReqT], Awaitable[ResT]],
    ) -> ResT:
        if not self._external:
            return await call(request)

        cached = cache.get(request)
        if cached is not None:
            return cached

        self._rate_limiter.check_and_consume(user_key)
        try:
            response = await call(request)
        except ProviderUnavailableError:
            return await fallback(request)

        cache.set(request, response)
        return response
