from app.schemes import AuthRequest, AuthResponse

from fastapi import APIRouter


router = APIRouter()


@router.post("/auth")
async def auth_user(auth_request: AuthRequest) -> AuthResponse:
    pass