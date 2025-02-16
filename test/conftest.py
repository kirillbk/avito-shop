from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import engine, get_db
from app.main import app, lifespan


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def db_test() -> AsyncGenerator[AsyncSession, None]:
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture
async def aclient(db_test) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = lambda: db_test

    async with lifespan(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac


@pytest.fixture
def user() -> dict[str, str]:
    return {
        "username": "user",
        "password": "password",
    }
