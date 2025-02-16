from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import engine, get_db
from app.main import app, lifespan
from app.services.repositories.transfer import TransferRepository
from app.services.repositories.user import UserRepository
from app.services.repositories.user_item import Item, UserItemRepository


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
def user1() -> dict[str, str]:
    return {
        "username": "aaaa",
        "password": "password",
    }


@pytest.fixture
def user2() -> dict[str, str]:
    return {
        "username": "bbbb",
        "password": "password",
    }


@pytest.fixture
async def auth_header(user1, aclient) -> dict[str, str]:
    resp = await aclient.post("api/auth", json=user1)
    token = resp.json()["token"]

    return {"Authorization": f"bearer {token}"}


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
def transfer_repo(db_test: AsyncSession) -> TransferRepository:
    return TransferRepository(db_test)
