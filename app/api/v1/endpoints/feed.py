from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_feed_service
from app.models.tweet import Tweet
from app.models.user import User
from app.schemas.feed import FeedTweetResponse
from app.services.feed import FeedService

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("", response_model=list[FeedTweetResponse])
async def get_feed(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    feed_service: FeedService = Depends(get_feed_service),
) -> list[Tweet]:
    return await feed_service.get_feed(current_user, limit, offset)
