from collections.abc import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

db_url = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.postgres_db,
)
engine = create_async_engine(db_url, echo=settings.debug)
session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session
