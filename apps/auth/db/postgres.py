from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from core.settings import settings

postgres_db_engine: AsyncEngine | None = None
async_session: async_sessionmaker[AsyncSession] | None = None

Base = declarative_base()

import models  # noqa: E402, F401


def setup_postgres_connection():
    global postgres_db_engine, async_session

    postgres_db_engine = create_async_engine(
        url=settings.postgres.URL,  # type: ignore
        pool_recycle=settings.postgres.POOL_RECYCLE,
        pool_size=settings.postgres.POOL_SIZE,
        echo=settings.postgres.ECHO,
    )

    async_session = async_sessionmaker(bind=postgres_db_engine, expire_on_commit=False)


async def close_postgres_connection():
    await postgres_db_engine.dispose()  # type: ignore


async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:  # type: ignore
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
