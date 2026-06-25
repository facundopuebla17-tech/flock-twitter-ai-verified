from uuid import UUID

from app.models.tweet import Tweet
from app.models.user import User
from app.repositories.tweet import TweetRepository
from app.schemas.tweet import TweetCreate


class TweetNotFoundError(Exception):
    """Raised when a requested tweet does not exist."""


class PermissionDeniedError(Exception):
    """Raised when a user is not allowed to modify a tweet."""


class TweetService:
    def __init__(self, tweet_repository: TweetRepository) -> None:
        self.tweet_repository = tweet_repository

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

    async def delete_tweet(self, tweet_id: UUID, user: User) -> None:
        tweet = await self.get_tweet(tweet_id)
        if tweet.author_id != user.id:
            raise PermissionDeniedError("You do not have permission to delete this tweet.")

        await self.tweet_repository.delete(tweet)
