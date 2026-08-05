"""AI endpoints under the /api/v1/ai prefix."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from app.ai.schemas import (
    InterpretSearchRequest,
    InterpretSearchResponse,
    ItineraryAiRequest,
    ItineraryAiResponse,
    OpportunitySummaryRequest,
    OpportunitySummaryResponse,
)
from app.api.deps import get_ai_service
from app.services.ai_service import AiService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])

AiServiceDep = Annotated[AiService, Depends(get_ai_service)]


def _user_key() -> str:
    """User identifier for quota and cache. Dev user until auth lands."""
    return "dev-user"


@router.post(
    "/opportunity-summary",
    response_model=OpportunitySummaryResponse,
)
async def opportunity_summary(
    payload: OpportunitySummaryRequest,
    service: AiServiceDep,
) -> OpportunitySummaryResponse:
    """Generate an orientative, structured summary for a travel opportunity.

    Falls back to a deterministic rule-based summary when the AI provider
    is disabled or fails. Never blocks the trip on an AI failure.
    """
    return await service.summarize_opportunity(payload, _user_key())


@router.post(
    "/interpret-search",
    response_model=InterpretSearchResponse,
)
async def interpret_search(
    payload: InterpretSearchRequest,
    service: AiServiceDep,
) -> InterpretSearchResponse:
    """Interpret a natural-language search into structured criteria."""
    return await service.interpret_search(payload, _user_key())


@router.post(
    "/itineraries",
    response_model=ItineraryAiResponse,
)
async def generate_itinerary(
    payload: ItineraryAiRequest,
    service: AiServiceDep,
) -> ItineraryAiResponse:
    """Generate an orientative structured itinerary from confirmed data."""
    return await service.generate_itinerary(payload, _user_key())
