"""Gemini-backed AI provider using the official google-genai SDK."""

from __future__ import annotations

import asyncio
import logging
from typing import TypeVar

from pydantic import BaseModel

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
from app.core.config import Settings
from app.core.errors import AiInvalidResponseError, ProviderUnavailableError

logger = logging.getLogger(__name__)

DEFAULT_RETRIES = 1
ResponseT = TypeVar("ResponseT", bound=BaseModel)


class GeminiAiProvider:
    """Calls Gemini from the backend only. Never exposes the API key."""

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model
        self._timeout_seconds = settings.gemini_timeout_seconds

    async def summarize_opportunity(
        self,
        request: OpportunitySummaryRequest,
    ) -> OpportunitySummaryResponse:
        return await self._with_retries(
            request_model=OpportunitySummaryResponse,
            prompt=self._build_summary_prompt(request),
        )

    async def interpret_search(
        self,
        request: InterpretSearchRequest,
    ) -> InterpretSearchResponse:
        return await self._with_retries(
            request_model=InterpretSearchResponse,
            prompt=self._build_interpret_prompt(request),
        )

    async def generate_itinerary(
        self,
        request: ItineraryAiRequest,
    ) -> ItineraryAiResponse:
        return await self._with_retries(
            request_model=ItineraryAiResponse,
            prompt=self._build_itinerary_prompt(request),
        )

    async def generate_daily_report(
        self,
        request: DailyReportRequest,
    ) -> DailyReportResponse:
        return await self._with_retries(
            request_model=DailyReportResponse,
            prompt=self._build_daily_report_prompt(request),
        )

    async def _with_retries(
        self,
        *,
        request_model: type[ResponseT],
        prompt: str,
    ) -> ResponseT:
        last_error: Exception | None = None
        attempts = DEFAULT_RETRIES + 1
        for attempt in range(attempts):
            try:
                result = await asyncio.to_thread(
                    self._generate_sync,
                    request_model,
                    prompt,
                )
                if isinstance(result, request_model):
                    return result
                raise AiInvalidResponseError()
            except Exception as exc:  # noqa: BLE001 - converted to domain errors below
                last_error = exc
                logger.warning(
                    "Gemini generation attempt %s/%s failed: %s",
                    attempt + 1,
                    attempts,
                    type(exc).__name__,
                )
        if isinstance(last_error, (AiInvalidResponseError, ProviderUnavailableError)):
            raise last_error
        raise ProviderUnavailableError() from last_error

    def _generate_sync(self, request_model: type[ResponseT], prompt: str) -> ResponseT:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=self._api_key,
            http_options=types.HttpOptions(timeout=int(self._timeout_seconds * 1000)),
        )
        response = client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=request_model,
            ),
        )
        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, request_model):
            return parsed
        text = getattr(response, "text", None)
        if text:
            return request_model.model_validate_json(text)
        raise AiInvalidResponseError()

    @staticmethod
    def _build_summary_prompt(request: OpportunitySummaryRequest) -> str:
        """Grounds the model with confirmed data and clear rules."""
        lines = [
            "You summarize a travel opportunity for a couple planning a budget getaway.",
            "Return strictly valid JSON matching the requested schema.",
            "",
            "CONFIRMED_PROVIDER_DATA:",
            f"- destination: {request.destination}",
            f"- total cost: {request.total_cost_eur:.2f} EUR for {request.travelers} travelers",
            f"- useful hours: {request.useful_hours:.1f}",
            f"- transport mode: {request.transport_mode.value}",
            f"- verified at: {request.verified_at.isoformat()}",
        ]
        for fact in request.facts:
            lines.append(f"- fact: {fact}")
        lines.extend(
            [
                "",
                "USER_PREFERENCES:",
                f"- budget for two: {request.budget_eur:.2f} EUR",
                "",
                "RULES:",
                "- Do not invent prices, availability, timetables or fees.",
                "- Mention unknown information explicitly.",
                "- The output must be a plain JSON object with no extra text.",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _build_interpret_prompt(request: InterpretSearchRequest) -> str:
        """Asks the model to structure a free-text search without inventing data."""
        return "\n".join(
            [
                "You convert a couple's travel search written in natural language into "
                "structured search criteria.",
                "Return strictly valid JSON matching the requested schema.",
                "",
                "USER_QUERY:",
                request.query,
                "",
                "RULES:",
                "- Only fill fields that are clearly expressed in the query.",
                "- Leave unknown fields null or empty.",
                "- Use the provided confidence values appropriately.",
                "- The output must be a plain JSON object with no extra text.",
            ]
        )

    @staticmethod
    def _build_itinerary_prompt(request: ItineraryAiRequest) -> str:
        """Builds an orientative itinerary from confirmed trip data."""
        lines = [
            "You create an orientative itinerary for a couple's trip.",
            "Return strictly valid JSON matching the requested schema.",
            "",
            "CONFIRMED_PROVIDER_DATA:",
            f"- destination: {request.destination}",
            f"- from: {request.start_date.isoformat()}",
            f"- to: {request.end_date.isoformat()}",
            f"- transport mode: {request.transport_mode.value}",
        ]
        for fact in request.facts:
            lines.append(f"- fact: {fact}")
        lines.extend(
            [
                "",
                "USER_PREFERENCES:",
                "- interests: "
                + (", ".join(request.interests) if request.interests else "not specified"),
                f"- budget: {request.budget_eur:.2f} EUR",
                "",
                "RULES:",
                "- Do not invent opening hours, prices or reservations.",
                "- If you are not sure, set estimated_cost_eur to null.",
                "- Keep estimated_cost_eur null unless a real provider confirmed it.",
                "- The output must be a plain JSON object with no extra text.",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _build_daily_report_prompt(request: DailyReportRequest) -> str:
        """Builds a grounded daily report from confirmed price history."""
        lines = [
            "You write a short, personalized daily report for a couple that watches trip prices.",
            "Return strictly valid JSON matching the requested schema.",
            "",
            "CONFIRMED_PROVIDER_DATA:",
            f"- report date: {request.report_date.isoformat()}",
        ]
        for index, watch in enumerate(request.watches, start=1):
            lines.append(f"- watch {index}: {watch.watch_name} -> {watch.destination}")
            lines.append(f"  current total: {watch.current_total_eur:.2f} EUR")
            if watch.previous_total_eur is not None:
                lines.append(f"  previous total: {watch.previous_total_eur:.2f} EUR")
            if watch.min_recorded_eur is not None:
                lines.append(f"  min recorded: {watch.min_recorded_eur:.2f} EUR")
            if watch.budget_eur is not None:
                lines.append(f"  budget: {watch.budget_eur:.2f} EUR")
            if watch.price_history:
                points = ", ".join(
                    f"{point.captured_at.date().isoformat()}={point.total_eur:.2f}"
                    for point in watch.price_history
                )
                lines.append(f"  history: {points}")
            for fact in watch.facts:
                lines.append(f"  fact: {fact}")
        lines.extend(
            [
                "",
                "RULES:",
                "- Only use the confirmed data above.",
                "- Never invent prices, availability, timetables or fees.",
                "- Compute change_eur and change_percent from the given numbers.",
                "- Mark is_new_low only when the current price is a new minimum.",
                "- Keep recommendations orientative, never financial advice.",
                "- The output must be a plain JSON object with no extra text.",
            ]
        )
        return "\n".join(lines)
