from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_tweet_service
from app.models.user import User
from app.schemas.tweet import TweetResponse
from app.schemas.user import UserResponse
from app.services.tweet import TweetService, UserNotFoundError

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}/tweets", response_model=list[TweetResponse])
async def list_user_tweets(
    user_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    tweet_service: TweetService = Depends(get_tweet_service),
) -> list[TweetResponse]:
    try:
        tweets = await tweet_service.list_tweets_by_author(user_id, limit, offset)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        ) from exc

    return [TweetResponse.model_validate(tweet) for tweet in tweets]
