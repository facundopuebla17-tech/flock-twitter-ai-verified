"""Data-access abstractions exported from this package."""

from app.repositories.feed import FeedRepository
from app.repositories.follow import FollowRepository
from app.repositories.like import LikeRepository
from app.repositories.tweet import TweetRepository
from app.repositories.user import UserRepository

__all__ = [
    "FeedRepository",
    "FollowRepository",
    "LikeRepository",
    "TweetRepository",
    "UserRepository",
]
