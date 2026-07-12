from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tweet import Tweet


class TweetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, tweet_data: Mapping[str, Any]) -> Tweet:
        tweet = Tweet(**tweet_data)
        self.session.add(tweet)
        await self.session.commit()
        await self.session.refresh(tweet)
        return tweet

    async def get_by_id(self, tweet_id: UUID) -> Tweet | None:
        return await self.session.get(Tweet, tweet_id)

    async def list_tweets(self, limit: int, offset: int) -> list[Tweet]:
        statement = select(Tweet).order_by(Tweet.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_tweets_by_author(
        self,
        author_id: UUID,
        limit: int,
        offset: int,
    ) -> list[Tweet]:
        statement = (
            select(Tweet)
            .where(Tweet.author_id == author_id)
            .order_by(Tweet.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def delete(self, tweet: Tweet) -> None:
        await self.session.delete(tweet)
        await self.session.commit()
