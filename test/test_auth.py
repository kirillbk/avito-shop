from http import HTTPStatus

import pytest
from httpx import AsyncClient
from jwt import decode

from app.config import settings
from test.check_error import check_error


@pytest.mark.anyio
class TestAuth:
    async def test_auth_new_user(self, user1: dict[str, str], aclient: AsyncClient):
        resp = await aclient.post("api/auth", json=user1)
        data = resp.json()
        token_data = decode(
            data["token"], settings.jwt_secret_key, (settings.jwt_algorithm,)
        )

        assert resp.status_code == HTTPStatus.OK
        assert token_data["sub"] == user1["username"]

    async def test_auth_ok(self, user1: dict[str, str], aclient: AsyncClient):
        await aclient.post("api/auth", json=user1)
        resp = await aclient.post("api/auth", json=user1)
        data = resp.json()
        token_data = decode(
            data["token"], settings.jwt_secret_key, (settings.jwt_algorithm,)
        )

        assert resp.status_code == HTTPStatus.OK
        assert token_data["sub"] == user1["username"]

    async def test_auth_fail(self, user1: dict[str, str], aclient: AsyncClient):
        await aclient.post("api/auth", json=user1)
        user1["password"] += "123"
        resp = await aclient.post("api/auth", json=user1)

        check_error(resp, HTTPStatus.UNAUTHORIZED)
