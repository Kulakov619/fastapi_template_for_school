from contextlib import asynccontextmanager

import uvicorn
from core.config import settings
from core.middleware import request_id_middleware
from db import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from api.v1 import examples, lib


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    yield
    await redis.redis.close()


app = FastAPI(
    title=settings.service_name,
    description="LIb API",
    version="1.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_id_middleware)

app.include_router(
    examples.router,
    prefix="/api/v1/examples",
    tags=["examples"],
)

app.include_router(
    lib.router,
    prefix="/api/v1/lib",
    tags=["lib"],
)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
