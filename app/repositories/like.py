from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.like import Like


class LikeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_like(self, user_id: UUID, tweet_id: UUID) -> Like | None:
        statement = select(Like).where(
            Like.user_id == user_id,
            Like.tweet_id == tweet_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create_like(self, user_id: UUID, tweet_id: UUID) -> Like:
        like = Like(user_id=user_id, tweet_id=tweet_id)
        self.session.add(like)
        await self.session.commit()
        await self.session.refresh(like)
        return like

    async def delete_like(self, like: Like) -> None:
        await self.session.delete(like)
        await self.session.commit()
