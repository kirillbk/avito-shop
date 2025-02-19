from http import HTTPStatus

import pytest
from httpx import AsyncClient

from app.auth import encode_jwt_token
from app.services.repositories.user import UserRepository
from app.services.repositories.user_item import Item, UserItemRepository
from test.check_error import check_error


@pytest.mark.anyio
class TestBuy:
    async def test_buy_one(
        self,
        username1: str,
        auth_header: dict[str, str],
        item: Item,
        aclient: AsyncClient,
        user_repo: UserRepository,
        user_item_repo: UserItemRepository,
    ):
        resp = await aclient.get(f"api/buy/{item.type}", headers=auth_header)
        assert resp.status_code == HTTPStatus.OK

        user = await user_repo.get(name=username1)
        assert user.coins == 1000 - item.price

        inventory = await user_item_repo.get_inventory(user.id)
        assert inventory[0]["type"] == item.type
        assert inventory[0]["quantity"] == 1

    async def test_buy_few(
        self,
        username1: str,
        auth_header: dict[str, str],
        item: Item,
        aclient: AsyncClient,
        user_repo: UserRepository,
        user_item_repo: UserItemRepository,
    ):
        for _ in range(3):
            resp = await aclient.get(f"api/buy/{item.type}", headers=auth_header)
            assert resp.status_code == HTTPStatus.OK

        user = await user_repo.get(name=username1)
        assert user.coins == 1000 - 3 * item.price

        inventory = await user_item_repo.get_inventory(user.id)
        assert inventory[0]["type"] == item.type
        assert inventory[0]["quantity"] == 3

    async def test_no_item(self, auth_header: dict[str, str], aclient: AsyncClient):
        resp = await aclient.get("api/buy/abcd", headers=auth_header)

        check_error(resp, HTTPStatus.BAD_REQUEST)

    async def test_no_coins(
        self, auth_header: dict[str, str], item: Item, aclient: AsyncClient
    ):
        for _ in range(3):
            resp = await aclient.get(f"api/buy/{item.type}", headers=auth_header)
            assert resp.status_code == HTTPStatus.OK

        resp = await aclient.get(f"api/buy/{item.type}", headers=auth_header)
        check_error(resp, HTTPStatus.BAD_REQUEST)

    async def test_unauthorized(self, username1: str, item: Item, aclient: AsyncClient):
        token = encode_jwt_token({"sub": username1})
        resp = await aclient.get(
            f"api/buy/{item.type}", headers={"Authorization": f"bearer {token}"}
        )

        check_error(resp, HTTPStatus.UNAUTHORIZED)
