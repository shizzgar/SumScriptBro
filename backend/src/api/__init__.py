from fastapi import APIRouter

from api.health import router as health_router
from api.telegram import router as telegram_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(telegram_router)
