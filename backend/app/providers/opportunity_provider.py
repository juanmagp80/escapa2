"""Travel opportunity provider contract.

The domain never couples to the raw JSON of an external provider: it only
depends on this protocol and the normalized domain models.
"""

from __future__ import annotations

import uuid
from typing import Protocol

from app.domain.opportunity import Opportunity, PriceSnapshot


class OpportunityProvider(Protocol):
    """Contract for sources that produce travel opportunities."""

    def list_opportunities(self) -> list[Opportunity]:
        """Return the currently known opportunities."""
        ...

    def get_opportunity(self, opportunity_id: uuid.UUID) -> Opportunity | None:
        """Return a single opportunity or None when unknown."""
        ...

    def price_history(
        self,
        opportunity_id: uuid.UUID,
    ) -> list[PriceSnapshot]:
        """Return price snapshots for an opportunity, oldest first."""
        ...

    def save_snapshots(self, snapshots: list[PriceSnapshot]) -> None:
        """Persist new price snapshots (idempotent by snapshot id)."""
        ...
