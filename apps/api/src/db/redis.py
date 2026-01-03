from redis.asyncio import Redis

redis: Redis | None = None


async def get_redis() -> Redis:
    if redis is None:
        raise RuntimeError("Redis connection is not initialized")
    return redis
