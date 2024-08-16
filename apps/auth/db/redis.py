from redis.asyncio import Redis

from core.settings import settings

redis: Redis | None = None


def setup_redis_connection():
    global redis
    redis = Redis(host=settings.redis.HOST, port=settings.redis.PORT)


async def close_redis_connection():
    await redis.close()  # type: ignore


async def get_redis() -> Redis | None:
    return redis
