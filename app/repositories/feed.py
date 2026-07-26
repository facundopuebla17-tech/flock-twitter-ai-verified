from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from app.models.follow import Follow
from app.models.tweet import Tweet
from app.models.user import User


class FeedRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_feed(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> list[Tweet]:
        following_ids = select(Follow.following_id).where(Follow.follower_id == user_id)
        statement = (
            select(Tweet)
            .join(Tweet.author)
            .options(
                contains_eager(Tweet.author).load_only(
                    User.id,
                    User.username,
                    User.avatar_url,
                )
            )
            .where(
                or_(
                    Tweet.author_id == user_id,
                    Tweet.author_id.in_(following_ids),
                )
            )
            .order_by(Tweet.created_at.desc(), Tweet.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())
