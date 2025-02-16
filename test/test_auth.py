from http import HTTPStatus

import pytest
from httpx import AsyncClient
from jwt import decode

from app.config import settings


@pytest.mark.anyio
class TestAuth:
    async def test_auth_new_user(
        self, user: dict[str, str], aclient: AsyncClient
    ):
        resp = await aclient.post("api/auth", json=user)
        data = resp.json()
        token_data = decode(
            data["token"], settings.jwt_secret_key, (settings.jwt_algorithm,)
        )

        assert resp.status_code == HTTPStatus.OK
        assert token_data["sub"] == user["username"]

    async def test_auth_ok(self, user: dict[str, str], aclient: AsyncClient):
        await aclient.post("api/auth", json=user)
        resp = await aclient.post("api/auth", json=user)
        data = resp.json()
        token_data = decode(
            data["token"], settings.jwt_secret_key, (settings.jwt_algorithm,)
        )

        assert resp.status_code == HTTPStatus.OK
        assert token_data["sub"] == user["username"]

    async def test_auth_fail(self, user: dict[str, str], aclient: AsyncClient):
        await aclient.post("api/auth", json=user)
        user["password"] += "123"
        resp = await aclient.post("api/auth", json=user)

        assert resp.status_code == HTTPStatus.UNAUTHORIZED
