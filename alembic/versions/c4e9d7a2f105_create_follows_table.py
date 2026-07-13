"""create follows table

Revision ID: c4e9d7a2f105
Revises: b8f3a2c91d47
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "c4e9d7a2f105"
down_revision = "b8f3a2c91d47"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "follows",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("follower_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("following_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["follower_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["following_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "follower_id",
            "following_id",
            name="uq_follows_follower_id_following_id",
        ),
    )
    op.create_index(
        op.f("ix_follows_follower_id"),
        "follows",
        ["follower_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follows_following_id"),
        "follows",
        ["following_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_follows_following_id"), table_name="follows")
    op.drop_index(op.f("ix_follows_follower_id"), table_name="follows")
    op.drop_table("follows")
