from functools import lru_cache
from typing import Callable, Type

from db.postgres import get_session
from db.redis import get_redis
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


def get_service(service_class: Type) -> Callable:
    @lru_cache()
    def service(
        redis: Redis = Depends(get_redis),
        pg: AsyncSession = Depends(get_session),
    ):
        return service_class(cache=redis, pg=pg)

    return service
