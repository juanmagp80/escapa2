"""vehicle_profiles table

Revision ID: 0006_vehicle_profile
Revises: 0005_notification_devices
Create Date: 2026-08-07

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_vehicle_profile"
down_revision: str | None = "0005_notification_devices"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vehicle_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("travel_profile_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("fuel_type", sa.String(length=20), nullable=False, server_default="GASOLINE"),
        sa.Column("average_consumption_l_per_100km", sa.Float(), nullable=True),
        sa.Column("tank_capacity_l", sa.Float(), nullable=True),
        sa.Column("estimated_cost_per_km_eur", sa.Float(), nullable=True),
        sa.Column("max_fuel_detour_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["travel_profile_id"],
            ["travel_profiles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_vehicle_profiles_travel_profile_id",
        "vehicle_profiles",
        ["travel_profile_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_vehicle_profiles_travel_profile_id",
        table_name="vehicle_profiles",
    )
    op.drop_table("vehicle_profiles")
