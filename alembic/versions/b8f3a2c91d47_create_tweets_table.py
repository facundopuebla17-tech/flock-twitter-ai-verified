"""create tweets table

Revision ID: b8f3a2c91d47
Revises: 547defd134b7
Create Date: 2026-06-24
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "b8f3a2c91d47"
down_revision = "547defd134b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tweets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.String(length=280), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tweets_author_id"), "tweets", ["author_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tweets_author_id"), table_name="tweets")
    op.drop_table("tweets")
