from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import engine, get_db
from app.main import app, lifespan

from app.service.repositories.user import UserRepository
from app.service.repositories.user_item import UserItemRepository
from app.service.repositories.item import Item, ItemRepository


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


@pytest.fixture
async def auth_header(user, aclient) -> AsyncGenerator[dict[str, str], None]:
    resp = await aclient.post("api/auth", json=user)
    token = resp.json()["token"]

    yield {"Authorization": f"bearer {token}"}


@pytest.fixture
async def item(db_test: AsyncSession) -> AsyncGenerator[Item]:
    item = Item(type="item", price=333)
    db_test.add(item)
    await db_test.commit()
    return item


@pytest.fixture
def user_repo(db_test: AsyncSession) -> UserRepository:
    return UserRepository(db_test)


@pytest.fixture
def user_item_repo(db_test: AsyncSession) -> UserItemRepository:
    return UserItemRepository(db_test)


@pytest.fixture
def item_repo(db_test: AsyncSession) -> ItemRepository:
    return ItemRepository(db_test)
