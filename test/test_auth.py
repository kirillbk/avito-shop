from http import HTTPStatus

import pytest
from httpx import AsyncClient
from jwt import decode

from app.config import settings
from app.schemes import AuthRequest
from test.check_error import check_error


@pytest.mark.anyio
class TestAuth:
    async def test_auth_new_user(self, auth_user1: AuthRequest, aclient: AsyncClient):
        resp = await aclient.post("api/auth", json=auth_user1.model_dump())
        data = resp.json()
        token_data = decode(
            data["token"], settings.jwt_secret_key, (settings.jwt_algorithm,)
        )

        assert resp.status_code == HTTPStatus.OK
        assert token_data["sub"] == auth_user1.username

    async def test_auth_ok(self, auth_user1: AuthRequest, aclient: AsyncClient):
        await aclient.post("api/auth", json=auth_user1.model_dump())
        resp = await aclient.post("api/auth", json=auth_user1.model_dump())
        data = resp.json()
        token_data = decode(
            data["token"], settings.jwt_secret_key, (settings.jwt_algorithm,)
        )

        assert resp.status_code == HTTPStatus.OK
        assert token_data["sub"] == auth_user1.username

    async def test_auth_fail(self, auth_user1: AuthRequest, aclient: AsyncClient):
        await aclient.post("api/auth", json=auth_user1.model_dump())
        auth_user1.password += "123"
        resp = await aclient.post("api/auth", json=auth_user1.model_dump())

        check_error(resp, HTTPStatus.UNAUTHORIZED)
