import datetime

from redis.asyncio import Redis

from core.settings import settings

redis_conn = Redis(host=settings.redis.HOST, port=settings.redis.PORT, db=5)


async def check_limit(user_id: str) -> bool:
    pipe = redis_conn.pipeline()
    now = datetime.datetime.now()
    key = f"{user_id}:{now.minute}"

    await pipe.incr(key, 1)
    await pipe.expire(key, 59)

    result = await pipe.execute()
    request_number = result[0]

    return request_number > settings.api.RPM_LIMIT
