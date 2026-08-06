"""add couple_id to search_watches

Revision ID: 0003_search_watch_couple_id
Revises: 0002_airports
Create Date: 2026-08-06

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_search_watch_couple_id"
down_revision: str | None = "0002_airports"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEV_COUPLE_ID = "00000000-0000-4000-8000-000000000001"


def upgrade() -> None:
    op.add_column(
        "search_watches",
        sa.Column(
            "couple_id",
            sa.Uuid(),
            nullable=False,
            server_default=sa.text(f"'{DEV_COUPLE_ID}'::uuid"),
        ),
    )


def downgrade() -> None:
    op.drop_column("search_watches", "couple_id")
