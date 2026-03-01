from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import check_db_connection, get_db_session
from core.redis import check_redis_connection, get_redis_client

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    checks: dict[str, bool]


@router.get("/live", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def liveness_probe() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_probe(
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> ReadinessResponse:
    _ = db
    _ = redis

    db_ready = await check_db_connection()
    redis_ready = await check_redis_connection()
    checks = {"database": db_ready, "redis": redis_ready}

    status_text = "ok" if all(checks.values()) else "degraded"
    return ReadinessResponse(status=status_text, checks=checks)
