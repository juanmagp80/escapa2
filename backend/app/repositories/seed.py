"""Seed helper for the database-backed vertical slice.

Reuses the reference data defined by the mock opportunity provider so that the
SQL backend behaves identically to the in-memory one.
"""

from __future__ import annotations

from app.providers.mock_opportunity_provider import MockOpportunityProvider
from app.repositories.sql_opportunity_repository import SqlOpportunityRepository


def seed_reference_opportunities(repository: SqlOpportunityRepository) -> None:
    """Persist the reference opportunities and their price snapshots."""
    mock = MockOpportunityProvider()
    repository.save_opportunities(mock.list_opportunities())
    for opportunity in mock.list_opportunities():
        repository.save_snapshots(mock.price_history(opportunity.id))
