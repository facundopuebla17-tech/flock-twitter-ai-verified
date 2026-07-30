from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.tweet import Tweet
    from app.models.user import User


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "tweet_id",
            name="uq_likes_user_id_tweet_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    tweet_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tweets.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    user: Mapped[User] = relationship(
        back_populates="likes",
        foreign_keys=[user_id],
    )
    tweet: Mapped[Tweet] = relationship(
        back_populates="likes",
        foreign_keys=[tweet_id],
    )
