from app.schemes import AuthRequest, AuthResponse
from app.store_service import StoreService
from app.auth_utils import encode_jwt_token

from fastapi import APIRouter, Depends

from typing import Annotated


router = APIRouter()


@router.post("/auth")
async def auth_user(
    auth_req: AuthRequest, store_service: Annotated[StoreService, Depends()]
) -> AuthResponse:
    user_id = await store_service.auth_user(auth_req.username, auth_req.password)
    token = encode_jwt_token(user_id)

    return AuthResponse(token=token)
