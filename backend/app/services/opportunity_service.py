"""Travel opportunity application service.

Holds filtering, sorting and lookup rules for opportunities and their price
history. It depends only on the provider protocol, never on a concrete source.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.core.errors import NotFoundError
from app.domain.enums import TransportMode
from app.domain.opportunity import Opportunity, PriceSnapshot
from app.providers.opportunity_provider import OpportunityProvider

_SORTABLE_FIELDS = {
    "total_cost_eur",
    "useful_hours",
    "cost_per_useful_hour_eur",
    "provider_verified_at",
}


class OpportunityQuery(BaseModel):
    """Query parameters for the opportunities list endpoint."""

    max_total_cost_eur: float | None = Field(default=None, ge=0)
    transport_mode: TransportMode | None = None
    start_after: datetime | None = None
    end_before: datetime | None = None
    destination: str | None = Field(default=None, max_length=120)
    origin: str | None = Field(default=None, max_length=120)
    interest: str | None = Field(default=None, max_length=40)
    min_useful_hours: float | None = Field(default=None, ge=0)
    sort: str | None = Field(default=None, max_length=40)

    @model_validator(mode="after")
    def _validate_sort(self) -> OpportunityQuery:
        if self.sort is not None:
            key = self.sort.lstrip("-")
            if key not in _SORTABLE_FIELDS:
                raise ValueError(
                    f"sort must be one of {sorted(_SORTABLE_FIELDS)}, optionally prefixed with '-'."
                )
        return self


class OpportunityService:
    """Application service exposing opportunity queries."""

    def __init__(self, provider: OpportunityProvider) -> None:
        self._provider = provider

    def list_opportunities(self, query: OpportunityQuery) -> list[Opportunity]:
        """Return opportunities matching the given query, sorted."""
        opportunities = self._provider.list_opportunities()
        filtered = [item for item in opportunities if self._matches(item, query)]
        return self._sort(filtered, query.sort)

    def get(self, opportunity_id: uuid.UUID) -> Opportunity:
        """Return a single opportunity or raise a domain error."""
        opportunity = self._provider.get_opportunity(opportunity_id)
        if opportunity is None:
            raise NotFoundError("opportunity", str(opportunity_id))
        return opportunity

    def price_history(self, opportunity_id: uuid.UUID) -> list[PriceSnapshot]:
        """Return the price history for an opportunity."""
        self.get(opportunity_id)
        return self._provider.price_history(opportunity_id)

    @staticmethod
    def _matches(item: Opportunity, query: OpportunityQuery) -> bool:
        if (
            query.max_total_cost_eur is not None
            and item.total_cost_eur is not None
            and item.total_cost_eur > query.max_total_cost_eur
        ):
            return False
        if query.transport_mode is not None and item.transport_mode != query.transport_mode:
            return False
        if query.start_after is not None and item.start_at < query.start_after:
            return False
        if query.end_before is not None and item.end_at > query.end_before:
            return False
        if query.destination is not None and query.destination.lower() not in (
            item.destination_name.lower()
        ):
            return False
        if query.origin is not None and (item.origin_city or "").lower() != query.origin.lower():
            return False
        if query.interest is not None and query.interest not in item.interests:
            return False
        if (
            query.min_useful_hours is not None
            and item.useful_hours is not None
            and item.useful_hours < query.min_useful_hours
        ):
            return False
        return True

    @staticmethod
    def _sort(opportunities: list[Opportunity], sort: str | None) -> list[Opportunity]:
        if sort is None:
            return opportunities
        descending = sort.startswith("-")
        key = sort.lstrip("-")

        def value(item: Opportunity) -> float:
            return float(getattr(item, key) or 0.0)

        return sorted(opportunities, key=value, reverse=descending)
