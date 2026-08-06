"""Tests for the SQLAlchemy repositories.

Use an in-memory SQLite database so no external service is required. The same
queries run against PostgreSQL in production.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from app.db.base import Base
from app.domain.availability import AvailabilityWindow
from app.domain.enums import FuelType, TransportMode, WindowKind
from app.domain.opportunity import Opportunity, PriceSnapshot
from app.domain.profile import AirportPreference
from app.repositories.seed import seed_reference_opportunities
from app.repositories.sql_availability_repository import SqlAvailabilityRepository
from app.repositories.sql_opportunity_repository import SqlOpportunityRepository
from app.repositories.sql_profile_repository import SqlProfileRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

PROFILE_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
OPPORTUNITY_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def test_profile_repository_creates_dev_profile_when_empty(session_factory) -> None:
    repository = SqlProfileRepository(session_factory)

    profile = repository.get_profile()

    assert profile.id == PROFILE_ID
    assert profile.origin_city == "Madrid"
    assert profile.default_budget_eur == 350.0

    airports = repository.get_airports()
    assert len(airports) == 2
    assert {airport.iata_code for airport in airports} == {"MAD", "BCN"}


def test_profile_repository_persists_updates(session_factory) -> None:
    repository = SqlProfileRepository(session_factory)
    initial = repository.get_profile()

    updated = repository.save_profile(
        initial.model_copy(
            update={
                "origin_city": "Barcelona",
                "default_budget_eur": 500.0,
                "updated_at": datetime.now(UTC),
            }
        )
    )

    assert updated.origin_city == "Barcelona"
    reloaded = repository.get_profile()
    assert reloaded.origin_city == "Barcelona"
    assert reloaded.default_budget_eur == 500.0


def test_profile_repository_replaces_airports(session_factory) -> None:
    repository = SqlProfileRepository(session_factory)
    profile = repository.get_profile()

    new_airports = [
        AirportPreference(
            id=uuid.uuid4(),
            travel_profile_id=profile.id,
            iata_code="AGP",
            enabled=True,
            transfer_cost_eur=25.0,
            transfer_minutes=20,
        ),
        AirportPreference(
            id=uuid.uuid4(),
            travel_profile_id=profile.id,
            iata_code="SVQ",
            enabled=True,
        ),
    ]

    stored = repository.save_airports(new_airports)
    assert len(stored) == 2

    reloaded = repository.get_airports()
    assert {airport.iata_code for airport in reloaded} == {"AGP", "SVQ"}
    assert reloaded[0].transfer_cost_eur == 25.0


def test_profile_repository_creates_and_updates_vehicle(session_factory) -> None:
    repository = SqlProfileRepository(session_factory)
    initial = repository.get_vehicle()

    assert initial.name == "Coche habitual"
    assert initial.fuel_type == FuelType.DIESEL
    assert initial.travel_profile_id == PROFILE_ID

    updated = repository.save_vehicle(
        initial.model_copy(
            update={
                "name": "Furgoneta",
                "fuel_type": FuelType.GASOLINE,
                "average_consumption_l_per_100km": 8.5,
                "tank_capacity_l": 60.0,
                "estimated_cost_per_km_eur": 0.14,
                "updated_at": datetime.now(UTC),
            }
        )
    )

    assert updated.name == "Furgoneta"
    reloaded = repository.get_vehicle()
    assert reloaded.name == "Furgoneta"
    assert reloaded.fuel_type == FuelType.GASOLINE
    assert reloaded.average_consumption_l_per_100km == 8.5


def test_availability_repository_crud(session_factory) -> None:
    repository = SqlAvailabilityRepository(session_factory)
    start = datetime.now(UTC)
    end = start + timedelta(days=2)
    window = AvailabilityWindow(
        id=uuid.uuid4(),
        start_at=start,
        end_at=end,
        kind=WindowKind.WEEKEND,
        is_flexible=True,
        created_at=start,
    )

    repository.create_window(window)
    assert repository.get_window(window.id) is not None

    updated_start = end + timedelta(days=1)
    updated_end = updated_start + timedelta(days=2)
    repository.update_window(
        window.model_copy(update={"start_at": updated_start, "end_at": updated_end})
    )
    reloaded = repository.get_window(window.id)
    assert reloaded is not None
    assert reloaded.start_at == updated_start

    assert len(repository.list_windows()) == 1
    assert repository.delete_window(window.id) is True
    assert repository.delete_window(window.id) is False
    assert len(repository.list_windows()) == 0


def test_opportunity_repository_seeds_reference_data(session_factory) -> None:
    repository = SqlOpportunityRepository(session_factory)
    seed_reference_opportunities(repository)

    opportunities = repository.list_opportunities()
    assert len(opportunities) == 4

    opportunity = repository.get_opportunity(OPPORTUNITY_ID)
    assert opportunity is not None
    assert opportunity.destination_name == "Santiago de Compostela"
    assert opportunity.transport_mode == TransportMode.CAR

    history = repository.price_history(OPPORTUNITY_ID)
    assert len(history) == 2
    assert history[0].captured_at <= history[1].captured_at


def test_opportunity_repository_saves_and_reads(session_factory) -> None:
    repository = SqlOpportunityRepository(session_factory)
    now = datetime.now(UTC)
    opportunity = Opportunity(
        id=uuid.uuid4(),
        destination_code="MAD",
        destination_name="Madrid",
        transport_mode=TransportMode.FLIGHT,
        start_at=now,
        end_at=now + timedelta(hours=40),
        useful_hours=30.0,
        total_cost_eur=210.0,
        cost_per_person_eur=105.0,
        cost_per_night_eur=105.0,
        cost_per_useful_hour_eur=7.0,
        provider_verified_at=now,
    )
    snapshot = PriceSnapshot(
        id=uuid.uuid4(),
        travel_opportunity_id=opportunity.id,
        total_cost_eur=210.0,
        flight_cost_eur=150.0,
        hotel_cost_eur=60.0,
        captured_at=now,
        source_summary_json={"provider": "test"},
    )

    repository.save_opportunities([opportunity])
    repository.save_snapshots([snapshot])

    assert repository.get_opportunity(opportunity.id) is not None
    assert len(repository.price_history(opportunity.id)) == 1
    assert repository.price_history(opportunity.id)[0].source_summary_json == {"provider": "test"}
