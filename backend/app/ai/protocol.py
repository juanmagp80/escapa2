"""AI provider contract."""

from __future__ import annotations

from typing import Protocol

from app.ai.schemas import (
    InterpretSearchRequest,
    InterpretSearchResponse,
    ItineraryAiRequest,
    ItineraryAiResponse,
    OpportunitySummaryRequest,
    OpportunitySummaryResponse,
)


class AiProvider(Protocol):
    """Contract for AI capabilities used by the application.

    The provider is responsible only for generating responses from
    confirmed/estimated data. It never acts as a source of prices.
    """

    async def summarize_opportunity(
        self,
        request: OpportunitySummaryRequest,
    ) -> OpportunitySummaryResponse:
        """Generate an orientative summary for a travel opportunity."""
        ...

    async def interpret_search(
        self,
        request: InterpretSearchRequest,
    ) -> InterpretSearchResponse:
        """Convert a natural-language search into structured criteria."""
        ...

    async def generate_itinerary(
        self,
        request: ItineraryAiRequest,
    ) -> ItineraryAiResponse:
        """Generate an orientative structured itinerary from confirmed data."""
        ...
