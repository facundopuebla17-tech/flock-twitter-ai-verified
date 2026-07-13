from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_follow_service, get_tweet_service
from app.models.user import User
from app.schemas.tweet import TweetResponse
from app.schemas.user import UserResponse, UserSummaryResponse
from app.services.exceptions import UserNotFoundError
from app.services.follow import (
    AlreadyFollowingError,
    CannotFollowYourselfError,
    FollowRelationshipNotFoundError,
    FollowService,
)
from app.services.tweet import TweetService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def follow_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    follow_service: FollowService = Depends(get_follow_service),
) -> None:
    try:
        await follow_service.follow_user(current_user, user_id)
    except UserNotFoundError as exc:
        raise _user_not_found_http_exception() from exc
    except CannotFollowYourselfError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself.",
        ) from exc
    except AlreadyFollowingError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already following this user.",
        ) from exc


@router.delete("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    follow_service: FollowService = Depends(get_follow_service),
) -> None:
    try:
        await follow_service.unfollow_user(current_user, user_id)
    except UserNotFoundError as exc:
        raise _user_not_found_http_exception() from exc
    except FollowRelationshipNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow relationship not found.",
        ) from exc


@router.get("/{user_id}/followers", response_model=list[UserSummaryResponse])
async def list_followers(
    user_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    follow_service: FollowService = Depends(get_follow_service),
) -> list[UserSummaryResponse]:
    try:
        followers = await follow_service.list_followers(user_id, limit, offset)
    except UserNotFoundError as exc:
        raise _user_not_found_http_exception() from exc

    return [UserSummaryResponse.model_validate(user) for user in followers]


@router.get("/{user_id}/following", response_model=list[UserSummaryResponse])
async def list_following(
    user_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    follow_service: FollowService = Depends(get_follow_service),
) -> list[UserSummaryResponse]:
    try:
        following = await follow_service.list_following(user_id, limit, offset)
    except UserNotFoundError as exc:
        raise _user_not_found_http_exception() from exc

    return [UserSummaryResponse.model_validate(user) for user in following]


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
        raise _user_not_found_http_exception() from exc

    return [TweetResponse.model_validate(tweet) for tweet in tweets]


def _user_not_found_http_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found.",
    )
