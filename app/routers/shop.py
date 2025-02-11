from app.schemes import InfoResponse, SendCoinRequest

from fastapi import APIRouter


router = APIRouter()


@router.get("/info")
async def get_user_info() -> InfoResponse:
    pass


@router.post("/sendCoin")
async def send_coin(send_request: SendCoinRequest):
    pass


@router.get("/buy/{item}")
async def buy_item(item: str):
    pass
