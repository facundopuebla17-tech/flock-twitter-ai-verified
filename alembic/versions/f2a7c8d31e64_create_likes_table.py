"""create likes table

Revision ID: f2a7c8d31e64
Revises: c4e9d7a2f105
Create Date: 2026-07-29
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "f2a7c8d31e64"
down_revision = "c4e9d7a2f105"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "likes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tweet_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tweet_id"], ["tweets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "tweet_id",
            name="uq_likes_user_id_tweet_id",
        ),
    )
    op.create_index(
        op.f("ix_likes_tweet_id"),
        "likes",
        ["tweet_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_likes_user_id"),
        "likes",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_likes_user_id"), table_name="likes")
    op.drop_index(op.f("ix_likes_tweet_id"), table_name="likes")
    op.drop_table("likes")
