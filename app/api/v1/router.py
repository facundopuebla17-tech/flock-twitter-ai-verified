from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.tweets import router as tweets_router
from app.api.v1.endpoints.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(tweets_router)
api_router.include_router(users_router)
