from datetime import UTC, datetime
from http import HTTPStatus

import pytest
from httpx import AsyncClient
from jwt import encode

from app.config import settings
from test.check_error import check_error


@pytest.mark.anyio
class TestSecurity:
    async def test_no_token(self, aclient: AsyncClient):
        resp = await aclient.get("api/buy/pen")

        check_error(resp, HTTPStatus.UNAUTHORIZED)

    async def test_bad_token(self, aclient: AsyncClient):
        resp = await aclient.get("api/buy/pen", headers={"Authorization": "X XX"})

        check_error(resp, HTTPStatus.UNAUTHORIZED)

    async def test_token_expired(self, username1: dict[str, str], aclient: AsyncClient):
        await aclient.post("api/auth", json=username1)

        token = encode(
            {"sub": username1["username"], "exp": datetime.now(UTC)},
            settings.jwt_secret_key,
            settings.jwt_algorithm,
        )
        resp = await aclient.get(
            "api/buy/pen", headers={"Authorization": f"bearer {token}"}
        )

        check_error(resp, HTTPStatus.UNAUTHORIZED)
