from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from api import api_router
from core.config import get_settings
from core.observability import setup_observability
from core.redis import redis_client


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await redis_client.close()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        lifespan=lifespan,
    )
    app.add_middleware(CorrelationIdMiddleware)

    app.include_router(api_router)
    setup_observability(app)

    return app


app = create_app()
