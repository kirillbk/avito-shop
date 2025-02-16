from app.auth import encode_jwt_token, JWTBearer
from app.schemes import (
    AuthRequest,
    AuthResponse,
    CoinHistorySchema,
    ErrorResponse,
    InfoResponse,
    SendCoinRequest,
)
from app.service.store import StoreService

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

from typing import Annotated


router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)

store_service_dep = Annotated[StoreService, Depends()]
current_user_dep = Annotated[str, Depends(JWTBearer())]


@router.post("/auth")
async def auth_user(
    auth_req: AuthRequest, store_service: store_service_dep
) -> AuthResponse:
    await store_service.auth_user(auth_req.username, auth_req.password)
    token = encode_jwt_token(auth_req.username)

    return AuthResponse(token=token)


@router.get("/info")
async def get_user_info(
    user: current_user_dep, store_service: store_service_dep
) -> InfoResponse:
    user_info = await store_service.get_user_info(user)

    resp = InfoResponse(
        coins=user_info["coins"],
        inventory=user_info["inventory"],
        coinHistory=CoinHistorySchema(
            received=user_info["received"], sent=user_info["sent"]
        ),
    )

    return resp


@router.post("/sendCoin", response_class=Response)
async def send_coin(
    send_req: SendCoinRequest, user: current_user_dep, store_service: store_service_dep
):
    await store_service.send_coin(user, send_req.toUser, send_req.amount)

    return Response()


@router.get("/buy/{item}", response_class=Response)
async def buy_item(item: str, user: current_user_dep, store_service: store_service_dep):
    await store_service.buy_item(user, item)

    return Response()
