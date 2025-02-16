from app.config import settings
from app.exceptions import UnauthorizedException

from fastapi import Request
from fastapi.security import HTTPBearer, utils
from jwt import encode, decode, PyJWTError

from datetime import datetime, timedelta, timezone


def encode_jwt_token(data: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_token_expire_minutes
    )
    token = encode(
        payload={"sub": data, "exp": expire},
        key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        headers={"alg": settings.jwt_algorithm, "typ": "JWT"},
    )

    return token


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
            raise UnauthorizedException(str(e))
        return data["sub"]
