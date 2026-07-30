from uuid import UUID

from app.models.tweet import Tweet
from app.models.user import User
from app.repositories.tweet import TweetRepository
from app.repositories.user import UserRepository
from app.schemas.tweet import TweetCreate
from app.services.exceptions import TweetNotFoundError, UserNotFoundError


class PermissionDeniedError(Exception):
    """Raised when a user is not allowed to modify a tweet."""


class TweetService:
    def __init__(
        self,
        tweet_repository: TweetRepository,
        user_repository: UserRepository,
    ) -> None:
        self.tweet_repository = tweet_repository
        self.user_repository = user_repository

    async def create_tweet(self, user: User, tweet_create: TweetCreate) -> Tweet:
        tweet_data = {
            "author_id": user.id,
            "content": tweet_create.content,
        }
        return await self.tweet_repository.create(tweet_data)

    async def get_tweet(self, tweet_id: UUID) -> Tweet:
        tweet = await self.tweet_repository.get_by_id(tweet_id)
        if tweet is None:
            raise TweetNotFoundError("Tweet not found.")

        return tweet

    async def list_tweets(self, limit: int, offset: int) -> list[Tweet]:
        return await self.tweet_repository.list_tweets(limit, offset)

    async def list_tweets_by_author(
        self,
        author_id: UUID,
        limit: int,
        offset: int,
    ) -> list[Tweet]:
        user = await self.user_repository.get_by_id(author_id)
        if user is None:
            raise UserNotFoundError("User not found.")

        return await self.tweet_repository.list_tweets_by_author(author_id, limit, offset)

    async def delete_tweet(self, tweet_id: UUID, user: User) -> None:
        tweet = await self.get_tweet(tweet_id)
        if tweet.author_id != user.id:
            raise PermissionDeniedError("You do not have permission to delete this tweet.")

        await self.tweet_repository.delete(tweet)
