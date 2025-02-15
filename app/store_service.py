from app.exceptions import UnauthorizedException
from app.config import settings
from app.models import User
from app.user_repository import UserRepository

from bcrypt import checkpw, gensalt, hashpw
from fastapi import Depends

from base64 import b64encode
from typing import Annotated
from hashlib import sha256


class StoreService:
    _user: UserRepository

    def __init__(self, user_repository: Annotated[UserRepository, Depends()]):
        self._user = user_repository

    async def auth_user(self, username: str, password: str):
        user = await self._user.get_user(name=username)
        password = sha256(password.encode()).digest()
        password = b64encode(password)
        if user and not checkpw(password, user.hashed_password.encode()):
            raise UnauthorizedException(f"Bad password for user <{username}>")
        if not user:
            hash = hashpw(password, gensalt()).decode()
            await self._user.add_user(username, hash) 
        