from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import api_router
from core.settings import settings
from db import postgres, redis


@asynccontextmanager
async def lifespan(_: FastAPI):
    postgres.setup_postgres_connection()
    redis.setup_redis_connection()
    yield
    await redis.close_redis_connection()
    await postgres.close_postgres_connection()


app = FastAPI(
    title=settings.api.TITLE,
    docs_url=settings.api.DOCS_URL,
    openapi_url=settings.api.OPENAPI_URL,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(api_router)
