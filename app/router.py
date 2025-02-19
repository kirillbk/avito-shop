from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

from app.auth import encode_jwt_token, get_current_user
from app.db.models import User
from app.schemes import (
    AuthRequest,
    AuthResponse,
    CoinHistorySchema,
    ErrorResponse,
    InfoResponse,
    SendCoinRequest,
)
from app.services.store import StoreService

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)

CurrentUser = Annotated[User, Depends(get_current_user)]
Service = Annotated[StoreService, Depends()]


@router.post("/auth")
async def auth_user(auth_req: AuthRequest, store_service: Service) -> AuthResponse:
    await store_service.auth_user(auth_req.username, auth_req.password)
    token = encode_jwt_token({"sub": auth_req.username})

    return AuthResponse(token=token)


@router.get("/info")
async def get_user_info(user: CurrentUser, store_service: Service) -> InfoResponse:
    user_info = await store_service.get_user_info(user)

    return InfoResponse(
        coins=user_info["coins"],
        inventory=user_info["inventory"],
        coinHistory=CoinHistorySchema(
            received=user_info["received"], sent=user_info["sent"]
        ),
    )


@router.post("/sendCoin", response_class=Response)
async def send_coin(
    send_req: SendCoinRequest,
    user: CurrentUser,
    store_service: Service,
):
    await store_service.send_coin(user, send_req.toUser, send_req.amount)

    return Response()


@router.get("/buy/{item}", response_class=Response)
async def buy_item(item: str, user: CurrentUser, store_service: Service):
    await store_service.buy_item(user, item)

    return Response()
