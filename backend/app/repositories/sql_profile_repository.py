"""SQLAlchemy repository for the couple travel profile.

Implements the ``ProfileProvider`` protocol on top of the ORM models. When no
profile exists yet it creates the same development profile that the mock
provider serves, so the API contract stays identical.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.domain.enums import TransportMode
from app.domain.profile import AirportPreference, TravelProfile
from app.models.airport_preference import AirportPreference as AirportPreferenceORM
from app.models.travel_profile import TravelProfile as TravelProfileORM
from app.repositories._util import as_utc

_DEV_PROFILE_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")


def _build_dev_profile() -> TravelProfile:
    now = datetime.now(UTC)
    return TravelProfile(
        id=_DEV_PROFILE_ID,
        origin_city="Madrid",
        currency="EUR",
        default_budget_eur=350.0,
        max_drive_minutes=240,
        preferred_transport=TransportMode.EITHER,
        interests=["ciudad", "gastronomía"],
        avoid_preferences=["vida nocturna"],
        created_at=now,
        updated_at=now,
    )


def _build_dev_airports() -> list[AirportPreference]:
    return [
        AirportPreference(
            id=uuid.UUID("00000000-0000-4000-8000-000000000002"),
            travel_profile_id=_DEV_PROFILE_ID,
            iata_code="MAD",
            enabled=True,
            transfer_cost_eur=12.0,
            transfer_minutes=45,
        ),
        AirportPreference(
            id=uuid.UUID("00000000-0000-4000-8000-000000000003"),
            travel_profile_id=_DEV_PROFILE_ID,
            iata_code="BCN",
            enabled=False,
            transfer_cost_eur=0.0,
            transfer_minutes=30,
        ),
    ]


class SqlProfileRepository:
    """Profile provider backed by the database."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def get_profile(self) -> TravelProfile:
        with self._session_factory() as session:
            row = session.execute(select(TravelProfileORM)).scalars().first()
            if row is None:
                profile = _build_dev_profile()
                self._ensure_profile(session, profile)
                self._ensure_airports(session, _build_dev_airports())
                session.commit()
                return profile
            return self._to_domain(row)

    def save_profile(self, profile: TravelProfile) -> TravelProfile:
        with self._session_factory() as session:
            row = (
                session.execute(select(TravelProfileORM).where(TravelProfileORM.id == profile.id))
                .scalars()
                .first()
            )
            if row is None:
                self._ensure_profile(session, profile)
                session.commit()
                return profile
            row.origin_city = profile.origin_city
            row.currency = profile.currency
            row.default_budget_eur = profile.default_budget_eur
            row.max_drive_minutes = profile.max_drive_minutes
            row.preferred_transport = profile.preferred_transport.value
            row.interests = profile.interests
            row.avoid_preferences = profile.avoid_preferences
            row.updated_at = profile.updated_at
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def get_airports(self) -> list[AirportPreference]:
        with self._session_factory() as session:
            profile = session.execute(select(TravelProfileORM)).scalars().first()
            if profile is None:
                self._ensure_profile(session, _build_dev_profile())
                airports = _build_dev_airports()
                self._ensure_airports(session, airports)
                session.commit()
                return airports
            rows = (
                session.execute(
                    select(AirportPreferenceORM).where(
                        AirportPreferenceORM.travel_profile_id == profile.id
                    )
                )
                .scalars()
                .all()
            )
            return [self._to_airport_domain(row) for row in rows]

    def save_airports(self, airports: list[AirportPreference]) -> list[AirportPreference]:
        with self._session_factory() as session:
            profile = session.execute(select(TravelProfileORM)).scalars().first()
            if profile is None:
                self._ensure_profile(session, _build_dev_profile())
            profile_id = profile.id if profile is not None else _DEV_PROFILE_ID
            session.execute(
                delete(AirportPreferenceORM).where(
                    AirportPreferenceORM.travel_profile_id == profile_id
                )
            )
            for airport in airports:
                session.add(
                    AirportPreferenceORM(
                        id=airport.id,
                        travel_profile_id=airport.travel_profile_id,
                        iata_code=airport.iata_code,
                        enabled=airport.enabled,
                        transfer_cost_eur=airport.transfer_cost_eur,
                        transfer_minutes=airport.transfer_minutes,
                    )
                )
            session.commit()
            return airports

    @staticmethod
    def _ensure_profile(session: Session, profile: TravelProfile) -> None:
        session.add(
            TravelProfileORM(
                id=profile.id,
                origin_city=profile.origin_city,
                currency=profile.currency,
                default_budget_eur=profile.default_budget_eur,
                max_drive_minutes=profile.max_drive_minutes,
                preferred_transport=profile.preferred_transport.value,
                interests=profile.interests,
                avoid_preferences=profile.avoid_preferences,
                created_at=profile.created_at,
                updated_at=profile.updated_at,
            )
        )

    @staticmethod
    def _ensure_airports(session: Session, airports: list[AirportPreference]) -> None:
        for airport in airports:
            session.add(
                AirportPreferenceORM(
                    id=airport.id,
                    travel_profile_id=airport.travel_profile_id,
                    iata_code=airport.iata_code,
                    enabled=airport.enabled,
                    transfer_cost_eur=airport.transfer_cost_eur,
                    transfer_minutes=airport.transfer_minutes,
                )
            )

    @staticmethod
    def _to_domain(row: TravelProfileORM) -> TravelProfile:
        return TravelProfile(
            id=row.id,
            origin_city=row.origin_city,
            currency=row.currency,
            default_budget_eur=row.default_budget_eur,
            max_drive_minutes=row.max_drive_minutes,
            preferred_transport=TransportMode(row.preferred_transport),
            interests=list(row.interests),
            avoid_preferences=list(row.avoid_preferences),
            created_at=as_utc(row.created_at),
            updated_at=as_utc(row.updated_at),
        )

    @staticmethod
    def _to_airport_domain(row: AirportPreferenceORM) -> AirportPreference:
        return AirportPreference(
            id=row.id,
            travel_profile_id=row.travel_profile_id,
            iata_code=row.iata_code,
            enabled=row.enabled,
            transfer_cost_eur=row.transfer_cost_eur,
            transfer_minutes=row.transfer_minutes,
        )
