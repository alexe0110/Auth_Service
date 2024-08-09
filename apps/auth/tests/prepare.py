from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from core.settings import settings
from db.postgres import get_postgres_session
from db.redis import get_redis
from main import app

dsn = (
    f"postgresql+asyncpg://{settings.postgres.USER}:{settings.postgres.PASSWORD}"
    f"@{settings.postgres.HOST}:5434/{settings.postgres.DB}"
)

engine: AsyncEngine = create_async_engine(dsn, poolclass=NullPool)
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, expire_on_commit=False)


async def override_get_session():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


def override_get_redis():
    return Redis(host=settings.redis.HOST, port=settings.redis.PORT, db=1)


app.dependency_overrides[get_postgres_session] = override_get_session
app.dependency_overrides[get_redis] = override_get_redis
