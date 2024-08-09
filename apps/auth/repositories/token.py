import abc
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from db.redis import get_redis


class TokenRepository(abc.ABC):
    @abc.abstractmethod
    async def setex(self, name: str, time: int, value: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_key(self, name):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_name(self, name):
        raise NotImplementedError


class RedisTokenRepository(TokenRepository):
    def __init__(self, redis: Annotated[Redis, Depends(get_redis)]) -> None:
        self.redis = redis

    async def setex(self, name: str, time: int, value: str):
        await self.redis.setex(name, time, value)

    async def delete_key(self, name):
        await self.redis.delete(name)

    async def get_by_name(self, name):
        return await self.redis.get(name)
