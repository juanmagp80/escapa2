"""notification devices

Revision ID: 0005_notification_devices
Revises: 0004_opportunity_details
Create Date: 2026-08-06

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_notification_devices"
down_revision: str | None = "0004_opportunity_details"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notification_devices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("token", sa.String(length=500), nullable=False),
        sa.Column("platform", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_devices_token", "notification_devices", ["token"], unique=True)
    op.create_index("ix_notification_devices_user_id", "notification_devices", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_notification_devices_user_id", table_name="notification_devices")
    op.drop_index("ix_notification_devices_token", table_name="notification_devices")
    op.drop_table("notification_devices")
