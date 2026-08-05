"""initial core tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-05

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "travel_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("origin_city", sa.String(length=120), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column("default_budget_eur", sa.Float(), nullable=True),
        sa.Column("max_drive_minutes", sa.Integer(), nullable=True),
        sa.Column(
            "preferred_transport",
            sa.String(length=20),
            nullable=False,
            server_default="EITHER",
        ),
        sa.Column("interests", sa.JSON(), nullable=False),
        sa.Column("avoid_preferences", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "availability_windows",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "kind",
            sa.String(length=20),
            nullable=False,
            server_default="WEEKEND",
        ),
        sa.Column("is_flexible", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "search_watches",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("criteria_json", sa.JSON(), nullable=False),
        sa.Column("alert_rules_json", sa.JSON(), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "travel_opportunities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("search_watch_id", sa.Uuid(), nullable=True),
        sa.Column("destination_code", sa.String(length=10), nullable=False),
        sa.Column("destination_name", sa.String(length=120), nullable=False),
        sa.Column("transport_mode", sa.String(length=20), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("useful_hours", sa.Float(), nullable=True),
        sa.Column("total_cost_eur", sa.Float(), nullable=True),
        sa.Column("cost_per_person_eur", sa.Float(), nullable=True),
        sa.Column("cost_per_night_eur", sa.Float(), nullable=True),
        sa.Column("cost_per_useful_hour_eur", sa.Float(), nullable=True),
        sa.Column("comfort_score", sa.Float(), nullable=True),
        sa.Column("value_score", sa.Float(), nullable=True),
        sa.Column("provider_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("travel_opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("total_cost_eur", sa.Float(), nullable=True),
        sa.Column("flight_cost_eur", sa.Float(), nullable=True),
        sa.Column("hotel_cost_eur", sa.Float(), nullable=True),
        sa.Column("route_cost_eur", sa.Float(), nullable=True),
        sa.Column("local_transport_cost_eur", sa.Float(), nullable=True),
        sa.Column("fees_cost_eur", sa.Float(), nullable=True),
        sa.Column(
            "captured_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("source_summary_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["travel_opportunity_id"],
            ["travel_opportunities.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_price_snapshots_travel_opportunity_id",
        "price_snapshots",
        ["travel_opportunity_id"],
    )

    op.create_table(
        "itineraries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("travel_opportunity_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("source_data_hash", sa.String(length=64), nullable=True),
        sa.Column("prompt_version", sa.String(length=40), nullable=True),
        sa.Column("model", sa.String(length=80), nullable=True),
        sa.Column("content_json", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["travel_opportunity_id"],
            ["travel_opportunities.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_itineraries_travel_opportunity_id",
        "itineraries",
        ["travel_opportunity_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_itineraries_travel_opportunity_id", table_name="itineraries")
    op.drop_table("itineraries")
    op.drop_index("ix_price_snapshots_travel_opportunity_id", table_name="price_snapshots")
    op.drop_table("price_snapshots")
    op.drop_table("travel_opportunities")
    op.drop_table("search_watches")
    op.drop_table("availability_windows")
    op.drop_table("travel_profiles")
