"""opportunity informational fields

Revision ID: 0004_opportunity_details
Revises: 0003_search_watch_couple_id
Create Date: 2026-08-06

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_opportunity_details"
down_revision: str | None = "0003_search_watch_couple_id"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "travel_opportunities",
        sa.Column("origin_city", sa.String(length=120), nullable=True),
    )
    op.add_column("travel_opportunities", sa.Column("interests", sa.JSON(), nullable=True))
    op.add_column("travel_opportunities", sa.Column("flight_cost_eur", sa.Float(), nullable=True))
    op.add_column("travel_opportunities", sa.Column("hotel_cost_eur", sa.Float(), nullable=True))
    op.add_column("travel_opportunities", sa.Column("route_cost_eur", sa.Float(), nullable=True))
    op.add_column(
        "travel_opportunities",
        sa.Column("booking_url", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("travel_opportunities", "booking_url")
    op.drop_column("travel_opportunities", "route_cost_eur")
    op.drop_column("travel_opportunities", "hotel_cost_eur")
    op.drop_column("travel_opportunities", "flight_cost_eur")
    op.drop_column("travel_opportunities", "interests")
    op.drop_column("travel_opportunities", "origin_city")
