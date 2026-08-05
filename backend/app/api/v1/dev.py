"""Development-only endpoints.

Enabled only when ``APP_ENV=development``. Never expose these in production.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import get_opportunity_provider
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.repositories.seed import seed_reference_opportunities
from app.repositories.sql_opportunity_repository import SqlOpportunityRepository

router = APIRouter(prefix="/dev", tags=["development"])


@router.post("/seed")
def seed() -> dict[str, object]:
    """Seed the database with the reference opportunities and snapshots."""
    settings = get_settings()
    if not settings.uses_sql_persistence:
        return {"seeded": False, "backend": "memory"}
    repository = SqlOpportunityRepository(SessionLocal)
    seed_reference_opportunities(repository)
    return {"seeded": True, "opportunities": len(repository.list_opportunities())}


@router.post("/reset")
def reset() -> dict[str, object]:
    """Force re-instantiation of providers with their default state."""
    from app.api import deps

    deps._opportunity_provider = None
    deps._profile_provider = None
    deps._availability_provider = None
    get_opportunity_provider()
    return {"reset": True}
