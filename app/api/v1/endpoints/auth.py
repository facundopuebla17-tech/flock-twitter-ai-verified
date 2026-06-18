from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_auth_service
from app.schemas.auth import Token, UserLogin
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import (
    AuthService,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UsernameAlreadyTakenError,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    try:
        user = await auth_service.register_user(user_create)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        ) from exc
    except UsernameAlreadyTakenError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken.",
        ) from exc

    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login_user(
    user_login: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    try:
        user = await auth_service.authenticate_user(user_login.email, user_login.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    access_token = auth_service.create_access_token(user)
    return Token(access_token=access_token, token_type="bearer")
