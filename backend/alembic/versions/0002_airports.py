"""airport_preferences table

Revision ID: 0002_airports
Revises: 0001_initial
Create Date: 2026-08-05

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_airports"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "airport_preferences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("travel_profile_id", sa.Uuid(), nullable=False),
        sa.Column("iata_code", sa.String(length=3), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("transfer_cost_eur", sa.Float(), nullable=True),
        sa.Column("transfer_minutes", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["travel_profile_id"],
            ["travel_profiles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_airport_preferences_travel_profile_id",
        "airport_preferences",
        ["travel_profile_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_airport_preferences_travel_profile_id",
        table_name="airport_preferences",
    )
    op.drop_table("airport_preferences")
