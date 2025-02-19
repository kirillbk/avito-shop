from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, utils
from jwt import PyJWTError, decode, encode

from app.config import settings
from app.db.models import User
from app.exceptions import UnauthorizedException
from app.services.store import StoreService


def encode_jwt_token(data: dict[Any]) -> str:
    data = data.copy()
    data["exp"] = datetime.now(UTC) + timedelta(
        minutes=settings.jwt_token_expire_minutes
    )
    return encode(
        payload=data,
        key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        headers={"alg": settings.jwt_algorithm, "typ": "JWT"},
    )


class JWTBearer(HTTPBearer):
    def __init__(self):
        super().__init__(bearerFormat="JWT")

    async def __call__(self, request: Request) -> str:
        authorization = request.headers.get("Authorization")
        scheme, credentials = utils.get_authorization_scheme_param(authorization)

        if not (authorization and scheme and credentials):
            raise UnauthorizedException("Not authenticated")
        if scheme.lower() != "bearer":
            raise UnauthorizedException("Invalid authentication credentials")

        try:
            data = decode(
                credentials, settings.jwt_secret_key, (settings.jwt_algorithm,)
            )
        except PyJWTError as e:
            raise UnauthorizedException(str(e)) from e
        return data


async def get_current_user(
    data: Annotated[dict[Any], Depends(JWTBearer())],
    store_servie: Annotated[StoreService, Depends()],
) -> User:
    user = await store_servie.get_user(data["sub"])
    if not user:
        raise UnauthorizedException(f"User <{data['sub']}> doesn't exist")

    return user
