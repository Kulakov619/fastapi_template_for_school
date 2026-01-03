from abc import ABC, abstractmethod
from typing import Any

import aiosmtplib
from core.config import settings
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


class Cache(ABC):
    """Abstract base class for caching."""

    @abstractmethod
    async def get(self, key: str) -> bytes | None:
        """Retrieve data from the cache."""
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: bytes, expire: int) -> None:
        """Store data in the cache."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete data in the cache."""
        raise NotImplementedError


class RedisCache(Cache):
    """Redis implementation of the Cache."""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> bytes | None:
        """Retrieve data from Redis."""
        return await self.redis.get(key)

    async def set(self, key: str, value: bytes, expire: int) -> None:
        """Store data in Redis."""
        await self.redis.set(key, value, expire)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)


class BaseService:
    def __init__(self, pg: AsyncSession, cache: Cache):
        self.db = pg
        self.cache = cache

    async def put_in_cache(self, key: str, value: Any, time: int = 60) -> None:
        await self.cache.set(key, value, time)

    async def check_in_cache(self, key: str) -> Any:
        cache = await self.cache.get(key)
        if not cache:
            return None
        return cache

    async def delete_from_cache(self, key: str) -> None:
        await self.cache.delete(key)
