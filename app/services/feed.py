from app.models.tweet import Tweet
from app.models.user import User
from app.repositories.feed import FeedRepository


class FeedService:
    def __init__(self, feed_repository: FeedRepository) -> None:
        self.feed_repository = feed_repository

    async def get_feed(
        self,
        current_user: User,
        limit: int,
        offset: int,
    ) -> list[Tweet]:
        return await self.feed_repository.list_feed(current_user.id, limit, offset)
