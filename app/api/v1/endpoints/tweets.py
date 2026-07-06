from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_tweet_service
from app.models.user import User
from app.schemas.tweet import TweetCreate, TweetResponse
from app.services.tweet import (
    PermissionDeniedError,
    TweetNotFoundError,
    TweetService,
)

router = APIRouter(prefix="/tweets", tags=["tweets"])


@router.post("", response_model=TweetResponse, status_code=status.HTTP_201_CREATED)
async def create_tweet(
    tweet_create: TweetCreate,
    current_user: User = Depends(get_current_user),
    tweet_service: TweetService = Depends(get_tweet_service),
) -> TweetResponse:
    tweet = await tweet_service.create_tweet(current_user, tweet_create)
    return TweetResponse.model_validate(tweet)


@router.get("", response_model=list[TweetResponse])
async def list_tweets(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    tweet_service: TweetService = Depends(get_tweet_service),
) -> list[TweetResponse]:
    tweets = await tweet_service.list_tweets(limit, offset)
    return [TweetResponse.model_validate(tweet) for tweet in tweets]


@router.get("/{tweet_id}", response_model=TweetResponse)
async def get_tweet(
    tweet_id: UUID,
    tweet_service: TweetService = Depends(get_tweet_service),
) -> TweetResponse:
    try:
        tweet = await tweet_service.get_tweet(tweet_id)
    except TweetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found.",
        ) from exc

    return TweetResponse.model_validate(tweet)


@router.delete("/{tweet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tweet(
    tweet_id: UUID,
    current_user: User = Depends(get_current_user),
    tweet_service: TweetService = Depends(get_tweet_service),
) -> None:
    try:
        await tweet_service.delete_tweet(tweet_id, current_user)
    except TweetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found.",
        ) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this tweet.",
        ) from exc
