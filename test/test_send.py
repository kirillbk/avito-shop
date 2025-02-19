from http import HTTPStatus

import pytest
from httpx import AsyncClient

from app.auth import encode_jwt_token
from app.schemes import AuthRequest
from app.services.repositories.transfer import TransferRepository
from app.services.repositories.user import UserRepository
from test.check_error import check_error


@pytest.mark.anyio
class TestSend:
    async def test_send(
        self,
        username1: str,
        auth_header: dict[str, str],
        auth_user2: AuthRequest,
        aclient: AsyncClient,
        user_repo: UserRepository,
        transfer_repo: TransferRepository,
    ):
        await aclient.post("api/auth", json=auth_user2.model_dump())
        resp = await aclient.post(
            "/api/sendCoin",
            json={"toUser": auth_user2.username, "amount": 333},
            headers=auth_header,
        )
        assert resp.status_code == HTTPStatus.OK

        from_user = await user_repo.get(name=username1)
        assert from_user.coins == 1000 - 333

        to_user = await user_repo.get(name=auth_user2.username)
        assert to_user.coins == 1000 + 333

        sent = await transfer_repo.get_sent(from_user.id)
        assert sent[0]["amount"] == 333
        assert sent[0]["name"] == to_user.name

        recieved = await transfer_repo.get_received(to_user.id)
        assert recieved[0]["amount"] == 333
        assert recieved[0]["name"] == from_user.name

    async def test_no_coins(
        self,
        auth_header: dict[str, str],
        auth_user2: AuthRequest,
        aclient: AsyncClient,
    ):
        await aclient.post("api/auth", json=auth_user2.model_dump())
        resp = await aclient.post(
            "/api/sendCoin",
            json={"toUser": auth_user2.username, "amount": 3333},
            headers=auth_header,
        )

        check_error(resp, HTTPStatus.BAD_REQUEST)

    async def test_unauthorized(
        self, username1: str, auth_user2: AuthRequest, aclient: AsyncClient
    ):
        await aclient.post("api/auth", json=auth_user2.model_dump())
        token = encode_jwt_token({"sub": username1})
        resp = await aclient.post(
            "api/sendCoin", headers={"Authorization": f"bearer {token}"}
        )

        check_error(resp, HTTPStatus.UNAUTHORIZED)

    async def test_no_to_user(
        self,
        auth_header: dict[str, str],
        username2: str,
        aclient: AsyncClient,
    ):
        resp = await aclient.post(
            "/api/sendCoin",
            json={"toUser": username2, "amount": 3333},
            headers=auth_header,
        )

        check_error(resp, HTTPStatus.BAD_REQUEST)
