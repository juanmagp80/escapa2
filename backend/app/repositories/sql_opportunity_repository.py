"""SQLAlchemy repository for travel opportunities and price history.

Implements the ``OpportunityProvider`` protocol on top of the ORM models.
Provides a ``seed_reference_data`` helper that mirrors the mock provider data
so the vertical slice works identically against the database.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import TransportMode
from app.domain.opportunity import Opportunity, PriceSnapshot
from app.models.price_snapshot import PriceSnapshot as PriceSnapshotORM
from app.models.travel_opportunity import TravelOpportunity as TravelOpportunityORM
from app.repositories._util import as_utc


class SqlOpportunityRepository:
    """Opportunity provider backed by the database."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def list_opportunities(self) -> list[Opportunity]:
        with self._session_factory() as session:
            rows = (
                session.execute(
                    select(TravelOpportunityORM).order_by(TravelOpportunityORM.total_cost_eur)
                )
                .scalars()
                .all()
            )
            return [self._to_domain(row) for row in rows]

    def get_opportunity(self, opportunity_id: uuid.UUID) -> Opportunity | None:
        with self._session_factory() as session:
            row = session.get(TravelOpportunityORM, opportunity_id)
            return self._to_domain(row) if row is not None else None

    def price_history(self, opportunity_id: uuid.UUID) -> list[PriceSnapshot]:
        with self._session_factory() as session:
            rows = (
                session.execute(
                    select(PriceSnapshotORM)
                    .where(PriceSnapshotORM.travel_opportunity_id == opportunity_id)
                    .order_by(PriceSnapshotORM.captured_at)
                )
                .scalars()
                .all()
            )
            return [self._to_snapshot_domain(row) for row in rows]

    def save_opportunities(self, opportunities: list[Opportunity]) -> None:
        """Insert or update the given opportunities."""
        with self._session_factory() as session:
            for opportunity in opportunities:
                row = session.get(TravelOpportunityORM, opportunity.id)
                if row is None:
                    session.add(self._to_orm(opportunity))
                else:
                    self._apply_to_orm(row, opportunity)
            session.commit()

    def save_snapshots(self, snapshots: list[PriceSnapshot]) -> None:
        """Insert or update the given price snapshots."""
        with self._session_factory() as session:
            for snapshot in snapshots:
                row = session.get(PriceSnapshotORM, snapshot.id)
                if row is None:
                    session.add(self._to_snapshot_orm(snapshot))
                else:
                    self._apply_to_snapshot_orm(row, snapshot)
            session.commit()

    @staticmethod
    def _to_orm(opportunity: Opportunity) -> TravelOpportunityORM:
        row = TravelOpportunityORM(id=opportunity.id)
        SqlOpportunityRepository._apply_to_orm(row, opportunity)
        return row

    @staticmethod
    def _apply_to_orm(
        row: TravelOpportunityORM,
        opportunity: Opportunity,
    ) -> None:
        row.destination_code = opportunity.destination_code
        row.destination_name = opportunity.destination_name
        row.transport_mode = opportunity.transport_mode.value
        row.start_at = opportunity.start_at
        row.end_at = opportunity.end_at
        row.useful_hours = opportunity.useful_hours
        row.total_cost_eur = opportunity.total_cost_eur
        row.cost_per_person_eur = opportunity.cost_per_person_eur
        row.cost_per_night_eur = opportunity.cost_per_night_eur
        row.cost_per_useful_hour_eur = opportunity.cost_per_useful_hour_eur
        row.comfort_score = opportunity.comfort_score
        row.value_score = opportunity.value_score
        row.provider_verified_at = opportunity.provider_verified_at

    @staticmethod
    def _to_snapshot_orm(snapshot: PriceSnapshot) -> PriceSnapshotORM:
        row = PriceSnapshotORM(id=snapshot.id)
        SqlOpportunityRepository._apply_to_snapshot_orm(row, snapshot)
        return row

    @staticmethod
    def _apply_to_snapshot_orm(
        row: PriceSnapshotORM,
        snapshot: PriceSnapshot,
    ) -> None:
        row.travel_opportunity_id = snapshot.travel_opportunity_id
        row.total_cost_eur = snapshot.total_cost_eur
        row.flight_cost_eur = snapshot.flight_cost_eur
        row.hotel_cost_eur = snapshot.hotel_cost_eur
        row.route_cost_eur = snapshot.route_cost_eur
        row.local_transport_cost_eur = snapshot.local_transport_cost_eur
        row.fees_cost_eur = snapshot.fees_cost_eur
        row.captured_at = snapshot.captured_at
        row.source_summary_json = snapshot.source_summary_json

    @staticmethod
    def _to_domain(row: TravelOpportunityORM) -> Opportunity:
        return Opportunity(
            id=row.id,
            destination_code=row.destination_code,
            destination_name=row.destination_name,
            transport_mode=TransportMode(row.transport_mode),
            start_at=as_utc(row.start_at),
            end_at=as_utc(row.end_at),
            useful_hours=row.useful_hours,
            total_cost_eur=row.total_cost_eur,
            cost_per_person_eur=row.cost_per_person_eur,
            cost_per_night_eur=row.cost_per_night_eur,
            cost_per_useful_hour_eur=row.cost_per_useful_hour_eur,
            comfort_score=row.comfort_score,
            value_score=row.value_score,
            provider_verified_at=(
                as_utc(row.provider_verified_at) if row.provider_verified_at is not None else None
            ),
        )

    @staticmethod
    def _to_snapshot_domain(row: PriceSnapshotORM) -> PriceSnapshot:
        return PriceSnapshot(
            id=row.id,
            travel_opportunity_id=row.travel_opportunity_id,
            total_cost_eur=row.total_cost_eur,
            flight_cost_eur=row.flight_cost_eur,
            hotel_cost_eur=row.hotel_cost_eur,
            route_cost_eur=row.route_cost_eur,
            local_transport_cost_eur=row.local_transport_cost_eur,
            fees_cost_eur=row.fees_cost_eur,
            captured_at=as_utc(row.captured_at),
            source_summary_json=dict(row.source_summary_json),
        )
