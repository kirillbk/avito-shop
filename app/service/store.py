from app.exceptions import BadRequestException, UnauthorizedException
from app.service.repositories.item import ItemRepository
from app.service.repositories.user_item import UserItemRepository
from app.service.repositories.user import UserRepository

from bcrypt import checkpw, gensalt, hashpw
from fastapi import Depends

from base64 import b64encode
from typing import Annotated
from hashlib import sha256


class StoreService:
    _item_repo: ItemRepository
    _user_repo: UserRepository

    def __init__(
        self,
        item_repository: Annotated[ItemRepository, Depends()],
        user_repository: Annotated[UserRepository, Depends()],
        user_item_repository: Annotated[UserItemRepository, Depends()],
    ):
        self._item_repo = item_repository
        self._user_repo = user_repository
        self._user_item_repo = user_item_repository

    async def auth_user(self, username: str, password: str):
        user = await self._user_repo.get_user(name=username)
        password = sha256(password.encode()).digest()
        password = b64encode(password)
        if user and not checkpw(password, user.hashed_password.encode()):
            raise UnauthorizedException(f"Bad password for user <{username}>")
        if not user:
            hash = hashpw(password, gensalt()).decode()
            await self._user_repo.add_user(username, hash)

    async def buy_item(self, username: str, item_type: str):
        user = await self._user_repo.get_user(name=username, lock=True)
        if not user:
            raise BadRequestException(f"User <{username}> doesn't exist")

        item = await self._item_repo.get_item(type=item_type)
        if not item:
            raise BadRequestException(f"Item <{item_type}> doesn't exist")
        if user.coins < item.price:
            raise BadRequestException(
                f"User <{username}> doesn't have enough coins to buy <{item_type}>"
            )

        user_item = await self._user_item_repo.get_item(
            user_id=user.id, item_id=item.id
        )
        if not user_item:
            await self._user_item_repo.add_item(user.id, item.id)
        else:
            await self._user_item_repo.update_qty(user_item.id, user_item.quantity + 1)

        await self._user_repo.update_coins(user.id, user.coins - item.price)

    async def send_coin(self, from_user: str, to_user: str, amount: int):
        pass
