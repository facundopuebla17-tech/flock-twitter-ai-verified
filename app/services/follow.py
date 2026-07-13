from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.models.follow import Follow
from app.models.user import User
from app.repositories.follow import FollowRepository
from app.repositories.user import UserRepository
from app.services.exceptions import UserNotFoundError


class CannotFollowYourselfError(Exception):
    """Raised when a user attempts to follow their own account."""


class AlreadyFollowingError(Exception):
    """Raised when a follow relationship already exists."""


class FollowRelationshipNotFoundError(Exception):
    """Raised when a requested follow relationship does not exist."""


class FollowService:
    def __init__(
        self,
        follow_repository: FollowRepository,
        user_repository: UserRepository,
    ) -> None:
        self.follow_repository = follow_repository
        self.user_repository = user_repository

    async def follow_user(self, current_user: User, target_user_id: UUID) -> Follow:
        if current_user.id == target_user_id:
            raise CannotFollowYourselfError("You cannot follow yourself.")

        await self._get_user(target_user_id)

        existing_follow = await self.follow_repository.get_follow(
            current_user.id,
            target_user_id,
        )
        if existing_follow is not None:
            raise AlreadyFollowingError("You are already following this user.")

        try:
            return await self.follow_repository.create_follow(
                current_user.id,
                target_user_id,
            )
        except IntegrityError as exc:
            await self.follow_repository.session.rollback()
            if self._is_duplicate_follow(exc):
                raise AlreadyFollowingError("You are already following this user.") from exc
            if self._is_missing_user(exc):
                raise UserNotFoundError("User not found.") from exc
            raise

    async def unfollow_user(self, current_user: User, target_user_id: UUID) -> None:
        await self._get_user(target_user_id)

        follow = await self.follow_repository.get_follow(current_user.id, target_user_id)
        if follow is None:
            raise FollowRelationshipNotFoundError("Follow relationship not found.")

        await self.follow_repository.delete_follow(follow)

    async def list_followers(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> list[User]:
        await self._get_user(user_id)
        return await self.follow_repository.list_followers(user_id, limit, offset)

    async def list_following(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> list[User]:
        await self._get_user(user_id)
        return await self.follow_repository.list_following(user_id, limit, offset)

    async def _get_user(self, user_id: UUID) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found.")
        return user

    @staticmethod
    def _is_duplicate_follow(error: IntegrityError) -> bool:
        constraint_name = FollowService._constraint_name(error)
        if constraint_name == "uq_follows_follower_id_following_id":
            return True

        error_message = str(error.orig).lower()
        return (
            "unique" in error_message
            and "follower_id" in error_message
            and "following_id" in error_message
        )

    @staticmethod
    def _is_missing_user(error: IntegrityError) -> bool:
        constraint_name = FollowService._constraint_name(error)
        if constraint_name in {
            "follows_follower_id_fkey",
            "follows_following_id_fkey",
        }:
            return True

        return "foreign key" in str(error.orig).lower()

    @staticmethod
    def _constraint_name(error: IntegrityError) -> str | None:
        diagnostic = getattr(error.orig, "diag", None)
        return getattr(diagnostic, "constraint_name", None)
