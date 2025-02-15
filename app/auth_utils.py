from app.config import settings

from jwt import encode, decode

from datetime import datetime, timedelta, timezone
from typing import Any


def encode_jwt_token(data: Any) -> str:
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


def decode_jwt_token(token: str) -> dict | None:
    decode(token, settings.jwt_secret_key, (settings.jwt_algorithm, ))
