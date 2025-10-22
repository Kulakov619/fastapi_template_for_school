import logging
import uuid
from contextvars import ContextVar

from core.config import settings
from fastapi import Request, status
from fastapi.responses import ORJSONResponse

request_id_var: ContextVar[str | None] = ContextVar("request_id")


async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")

    if request.url.path in settings.request_id_excluded_urls:
        return await call_next(request)

    if not request_id:
        if settings.dev_enviroment:
            request_id = uuid.uuid4().hex[:28]
        else:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "X-Request-Id is required"},
            )

    request_id_var.set(request_id)
    logger = logging.getLogger(__name__)
    if not settings.dev_enviroment:
        logger.info(f"Request started: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"Request failed: {request.method} {request.url.path}", exc_info=True)
        raise

    response.headers["X-Request-Id"] = request_id
    if not settings.dev_enviroment:
        logger.info(f"Request finished: {request.method} {request.url.path}")
    return response

