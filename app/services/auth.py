from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate

password_context = CryptContext(schemes=["argon2"], deprecated="auto")


class EmailAlreadyRegisteredError(Exception):
    """Raised when attempting to register with an email that already exists."""


class UsernameAlreadyTakenError(Exception):
    """Raised when attempting to register with a username that already exists."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials do not match a user."""


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.user_repository.get_by_email(email)
        if user is None or not self.verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password.")

        return user

    def create_access_token(self, user: User) -> str:
        expires_at = datetime.now(UTC) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "exp": expires_at,
        }
        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        return password_context.verify(plain_password, password_hash)

    async def register_user(self, user_create: UserCreate) -> User:
        existing_user_by_email = await self.user_repository.get_by_email(user_create.email)
        if existing_user_by_email is not None:
            raise EmailAlreadyRegisteredError("Email is already registered.")

        existing_user_by_username = await self.user_repository.get_by_username(
            user_create.username
        )
        if existing_user_by_username is not None:
            raise UsernameAlreadyTakenError("Username is already taken.")

        user_data = {
            "email": str(user_create.email),
            "username": user_create.username,
            "password_hash": password_context.hash(user_create.password),
        }

        try:
            user = await self.user_repository.create(user_data)
        except IntegrityError as exc:
            await self.user_repository.session.rollback()
            self._raise_for_unique_violation(exc)
            raise

        return user

    def _raise_for_unique_violation(self, error: IntegrityError) -> None:
        error_message = str(error.orig).lower() if error.orig is not None else str(error).lower()

        if self._matches_email_constraint(error_message):
            raise EmailAlreadyRegisteredError("Email is already registered.") from error

        if self._matches_username_constraint(error_message):
            raise UsernameAlreadyTakenError("Username is already taken.") from error

    @staticmethod
    def _matches_email_constraint(error_message: str) -> bool:
        return "users_email_key" in error_message or "email" in error_message

    @staticmethod
    def _matches_username_constraint(error_message: str) -> bool:
        return "users_username_key" in error_message or "username" in error_message
