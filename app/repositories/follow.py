from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.follow import Follow
from app.models.user import User


class FollowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_follow(self, follower_id: UUID, following_id: UUID) -> Follow:
        follow = Follow(follower_id=follower_id, following_id=following_id)
        self.session.add(follow)
        await self.session.commit()
        await self.session.refresh(follow)
        return follow

    async def get_follow(self, follower_id: UUID, following_id: UUID) -> Follow | None:
        statement = select(Follow).where(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def delete_follow(self, follow: Follow) -> None:
        await self.session.delete(follow)
        await self.session.commit()

    async def list_followers(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> list[User]:
        statement = (
            select(User)
            .join(Follow, User.id == Follow.follower_id)
            .where(Follow.following_id == user_id)
            .order_by(Follow.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_following(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> list[User]:
        statement = (
            select(User)
            .join(Follow, User.id == Follow.following_id)
            .where(Follow.follower_id == user_id)
            .order_by(Follow.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())
