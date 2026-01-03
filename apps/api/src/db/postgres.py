from typing import AsyncGenerator

from core.config import settings
from sqlalchemy import String
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase

from .annotations import str_50, str_255


class Base(DeclarativeBase):
    type_annotation_map = {
        str_255: String(255),
        str_50: String(50),
    }


dsn = settings.db_full_url


engine = create_async_engine(
    dsn,
    echo=settings.db_engine_echo,
    pool_pre_ping=True,
    pool_recycle=3600,
)


async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine() -> None:
    await engine.dispose()
