from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import settings
from app.db.db import get_db
from app.db.models import Base
from app.main import app, lifespan
from app.services.repositories.transfer import TransferRepository
from app.services.repositories.user import UserRepository
from app.services.repositories.user_item import Item, UserItemRepository


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def db_test() -> AsyncGenerator[AsyncSession, None]:
    db_url = URL.create(
        drivername="postgresql+asyncpg",
        username=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_test_db,
    )
    engine = create_async_engine(db_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

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
async def item(db_test: AsyncSession) -> Item:
    item = Item(type="xxxx", price=333)
    db_test.add(item)
    await db_test.commit()
    return item


@pytest.fixture
async def items(db_test: AsyncSession) -> list[Item]:
    items = [
        Item(type="aaa", price=200),
        Item(type="bbb", price=100),
        Item(type="ccc", price=50),
    ]
    db_test.add_all(items)
    await db_test.commit()
    return items


@pytest.fixture
def user_repo(db_test: AsyncSession) -> UserRepository:
    return UserRepository(db_test)


@pytest.fixture
def user_item_repo(db_test: AsyncSession) -> UserItemRepository:
    return UserItemRepository(db_test)


@pytest.fixture
def transfer_repo(db_test: AsyncSession) -> TransferRepository:
    return TransferRepository(db_test)
