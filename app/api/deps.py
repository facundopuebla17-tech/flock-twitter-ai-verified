from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.user import User
from app.repositories.feed import FeedRepository
from app.repositories.follow import FollowRepository
from app.repositories.tweet import TweetRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService, InvalidTokenError
from app.services.feed import FeedService
from app.services.follow import FollowService
from app.services.tweet import TweetService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)


def get_tweet_repository(session: AsyncSession = Depends(get_db_session)) -> TweetRepository:
    return TweetRepository(session)


def get_follow_repository(session: AsyncSession = Depends(get_db_session)) -> FollowRepository:
    return FollowRepository(session)


def get_feed_repository(session: AsyncSession = Depends(get_db_session)) -> FeedRepository:
    return FeedRepository(session)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository)


def get_tweet_service(
    tweet_repository: TweetRepository = Depends(get_tweet_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> TweetService:
    return TweetService(tweet_repository, user_repository)


def get_follow_service(
    follow_repository: FollowRepository = Depends(get_follow_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> FollowService:
    return FollowService(follow_repository, user_repository)


def get_feed_service(
    feed_repository: FeedRepository = Depends(get_feed_repository),
) -> FeedService:
    return FeedService(feed_repository)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        return await auth_service.get_user_from_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
