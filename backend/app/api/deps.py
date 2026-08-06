"""Shared FastAPI dependencies."""

from __future__ import annotations

from app.ai.factory import build_ai_provider
from app.ai.protocol import AiProvider
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.providers.availability_provider import AvailabilityProvider
from app.providers.mock_availability_provider import MockAvailabilityProvider
from app.providers.mock_opportunity_provider import MockOpportunityProvider
from app.providers.mock_profile_provider import MockProfileProvider
from app.providers.mock_search_watch_provider import MockSearchWatchProvider
from app.providers.opportunity_provider import OpportunityProvider
from app.providers.profile_provider import ProfileProvider
from app.providers.search_watch_provider import SearchWatchProvider
from app.repositories.seed import seed_reference_opportunities
from app.repositories.sql_availability_repository import SqlAvailabilityRepository
from app.repositories.sql_opportunity_repository import SqlOpportunityRepository
from app.repositories.sql_profile_repository import SqlProfileRepository
from app.repositories.sql_search_watch_repository import SqlSearchWatchRepository
from app.services.ai_service import AiService
from app.services.availability_service import AvailabilityService
from app.services.opportunity_service import OpportunityService
from app.services.profile_service import ProfileService
from app.services.radar_scheduler import RadarScheduler
from app.services.search_watch_service import SearchWatchService

_ai_provider: AiProvider | None = None
_ai_service: AiService | None = None
_opportunity_provider: OpportunityProvider | None = None
_profile_provider: ProfileProvider | None = None
_availability_provider: AvailabilityProvider | None = None
_search_watch_provider: SearchWatchProvider | None = None
_search_watch_service: SearchWatchService | None = None


def get_ai_provider() -> AiProvider:
    """Return a process-wide AI provider instance."""
    global _ai_provider
    if _ai_provider is None:
        _ai_provider = build_ai_provider(get_settings())
    return _ai_provider


def get_ai_service() -> AiService:
    """Return a process-wide AI service with quota, cache and fallback."""
    global _ai_service
    if _ai_service is None:
        settings = get_settings()
        _ai_service = AiService(
            get_ai_provider(),
            max_requests_per_user_day=settings.gemini_max_requests_per_user_day,
            model=settings.gemini_model,
        )
    return _ai_service


def get_opportunity_provider() -> OpportunityProvider:
    """Return a process-wide opportunity provider instance.

    Uses the mock provider by default. When ``PERSISTENCE_BACKEND=sql`` it uses
    the database, seeding the reference opportunities on first use.
    """
    global _opportunity_provider
    if _opportunity_provider is None:
        settings = get_settings()
        if settings.uses_sql_persistence:
            repository = SqlOpportunityRepository(SessionLocal)
            seed_reference_opportunities(repository)
            _opportunity_provider = repository
        else:
            _opportunity_provider = MockOpportunityProvider()
    return _opportunity_provider


def get_opportunity_service() -> OpportunityService:
    """Return the opportunity application service."""
    return OpportunityService(get_opportunity_provider())


def get_profile_provider() -> ProfileProvider:
    """Return a process-wide profile provider instance.

    Uses the mock provider by default. When ``PERSISTENCE_BACKEND=sql`` it uses
    the database.
    """
    global _profile_provider
    if _profile_provider is None:
        settings = get_settings()
        if settings.uses_sql_persistence:
            _profile_provider = SqlProfileRepository(SessionLocal)
        else:
            _profile_provider = MockProfileProvider()
    return _profile_provider


def get_profile_service() -> ProfileService:
    """Return the profile application service."""
    return ProfileService(get_profile_provider())


def get_availability_provider() -> AvailabilityProvider:
    """Return a process-wide availability provider instance.

    Uses the mock provider by default. When ``PERSISTENCE_BACKEND=sql`` it uses
    the database.
    """
    global _availability_provider
    if _availability_provider is None:
        settings = get_settings()
        if settings.uses_sql_persistence:
            _availability_provider = SqlAvailabilityRepository(SessionLocal)
        else:
            _availability_provider = MockAvailabilityProvider()
    return _availability_provider


def get_availability_service() -> AvailabilityService:
    """Return the availability application service."""
    return AvailabilityService(get_availability_provider())


def get_search_watch_provider() -> SearchWatchProvider:
    """Return a process-wide search watch provider instance.

    Uses the mock provider by default. When ``PERSISTENCE_BACKEND=sql`` it uses
    the database.
    """
    global _search_watch_provider
    if _search_watch_provider is None:
        settings = get_settings()
        if settings.uses_sql_persistence:
            _search_watch_provider = SqlSearchWatchRepository(SessionLocal)
        else:
            _search_watch_provider = MockSearchWatchProvider()
    return _search_watch_provider


def get_search_watch_service() -> SearchWatchService:
    """Return the search watch application service."""
    global _search_watch_service
    if _search_watch_service is None:
        _search_watch_service = SearchWatchService(
            get_search_watch_provider(),
            get_opportunity_provider(),
        )
    return _search_watch_service


def get_radar_scheduler() -> RadarScheduler:
    """Return the radar scheduler, created but not started.

    The scheduler only starts when ``SCHEDULER_ENABLED=true`` (see main.py
    lifespan). Tests keep it idle because the flag defaults to false.
    """
    settings = get_settings()
    return RadarScheduler(
        get_search_watch_service(),
        interval_seconds=settings.scheduler_interval_seconds,
    )
