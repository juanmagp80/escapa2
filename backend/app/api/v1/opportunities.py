"""Opportunities API under the /api/v1/opportunities prefix."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_opportunity_service
from app.domain.opportunity import Opportunity, PriceSnapshot
from app.services.opportunity_service import OpportunityQuery, OpportunityService

router = APIRouter(prefix="/opportunities", tags=["opportunities"])

OpportunityServiceDep = Annotated[OpportunityService, Depends(get_opportunity_service)]


@router.get("", response_model=list[Opportunity])
def list_opportunities(
    query: Annotated[OpportunityQuery, Query()],
    service: OpportunityServiceDep,
) -> list[Opportunity]:
    """List opportunities, optionally filtered and sorted."""
    return service.list_opportunities(query)


@router.get("/{opportunity_id}", response_model=Opportunity)
def get_opportunity(
    opportunity_id: uuid.UUID,
    service: OpportunityServiceDep,
) -> Opportunity:
    """Return a single opportunity."""
    return service.get(opportunity_id)


@router.get("/{opportunity_id}/price-history", response_model=list[PriceSnapshot])
def get_price_history(
    opportunity_id: uuid.UUID,
    service: OpportunityServiceDep,
) -> list[PriceSnapshot]:
    """Return the price history of an opportunity, oldest first."""
    return service.price_history(opportunity_id)
