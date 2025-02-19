from http import HTTPStatus

import pytest
from httpx import AsyncClient, Response

from app.auth import encode_jwt_token
from app.db.models import Item
from app.schemes import AuthRequest
from test.check_error import check_error


@pytest.mark.anyio
class TestInfo:
    async def test_info(
        self,
        username1: str,
        auth_header: dict[str, str],
        auth_user2: AuthRequest,
        items: list[Item],
        aclient: AsyncClient,
    ):
        def _test_info_response(resp: Response):
            info = resp.json()
            assert len(info) == 3

            assert info["coins"] == 1000 - total_spent

            inventory = info["inventory"]
            assert len(inventory) == len(items)
            assert sum(item["quantity"] for item in inventory) == 6
            for i in range(3):
                assert len(inventory[i]) == 2
                assert inventory[i]["type"] == items[i].type

            assert len(info["coinHistory"]) == 2
            sent = info["coinHistory"]["sent"]
            assert len(sent) == 3
            received = info["coinHistory"]["received"]
            assert len(received) == 3
            for i in range(3):
                assert len(sent[i]) == 2
                assert len(received[i]) == 2
                assert sent[i]["amount"] == received[i]["amount"]
                assert (
                    sent[i]["toUser"] == received[i]["fromUser"] == auth_user2.username
                )
            assert sum(t["amount"] for t in sent) == total_sent

        # buy items
        total_spent = 0
        for i, item in enumerate(items, 1):
            for _ in range(i):
                total_spent += item.price
                await aclient.get(f"api/buy/{item.type}", headers=auth_header)

        # make transactions
        resp = await aclient.post("api/auth", json=auth_user2.model_dump())
        user2_token = resp.json()["token"]
        user2_auth_header = {"Authorization": f"bearer {user2_token}"}
        total_sent = 0
        for amount in range(10, 40, 10):
            total_sent += amount
            await aclient.post(
                "/api/sendCoin",
                json={"toUser": auth_user2.username, "amount": amount},
                headers=auth_header,
            )
            await aclient.post(
                "/api/sendCoin",
                json={"toUser": username1, "amount": amount},
                headers=user2_auth_header,
            )

        resp = await aclient.get("api/info", headers=auth_header)
        assert resp.status_code == HTTPStatus.OK

        _test_info_response(resp)

    async def test_unauthorized(self, username1: str, aclient: AsyncClient):
        token = encode_jwt_token({"sub": username1})
        resp = await aclient.get(
            "api/info", headers={"Authorization": f"bearer {token}"}
        )

        check_error(resp, HTTPStatus.UNAUTHORIZED)
