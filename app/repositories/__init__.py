"""Data-access abstractions exported from this package."""

from app.repositories.tweet import TweetRepository
from app.repositories.user import UserRepository

__all__ = ["TweetRepository", "UserRepository"]
