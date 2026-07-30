from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.repositories.like import LikeRepository
from app.repositories.tweet import TweetRepository
from app.services.exceptions import TweetNotFoundError


class LikeService:
    def __init__(
        self,
        like_repository: LikeRepository,
        tweet_repository: TweetRepository,
    ) -> None:
        self.like_repository = like_repository
        self.tweet_repository = tweet_repository

    async def like_tweet(self, current_user: User, tweet_id: UUID) -> None:
        await self._ensure_tweet_exists(tweet_id)

        like = await self.like_repository.get_like(current_user.id, tweet_id)
        if like is not None:
            return

        try:
            await self.like_repository.create_like(current_user.id, tweet_id)
        except IntegrityError as exc:
            await self.like_repository.session.rollback()
            if self._is_duplicate_like(exc):
                return
            raise

    async def unlike_tweet(self, current_user: User, tweet_id: UUID) -> None:
        await self._ensure_tweet_exists(tweet_id)

        like = await self.like_repository.get_like(current_user.id, tweet_id)
        if like is None:
            return

        await self.like_repository.delete_like(like)

    async def _ensure_tweet_exists(self, tweet_id: UUID) -> None:
        tweet = await self.tweet_repository.get_by_id(tweet_id)
        if tweet is None:
            raise TweetNotFoundError("Tweet not found.")

    @staticmethod
    def _is_duplicate_like(error: IntegrityError) -> bool:
        diagnostic = getattr(error.orig, "diag", None)
        constraint_name = getattr(diagnostic, "constraint_name", None)
        if constraint_name == "uq_likes_user_id_tweet_id":
            return True

        error_message = str(error.orig).lower()
        return (
            "unique" in error_message
            and "user_id" in error_message
            and "tweet_id" in error_message
        )
