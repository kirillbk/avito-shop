from base64 import b64encode
from hashlib import sha256
from typing import Annotated, Any

from bcrypt import checkpw, gensalt, hashpw
from fastapi import Depends

from app.db.models import User
from app.exceptions import BadRequestException, UnauthorizedException
from app.services.repositories.item import ItemRepository
from app.services.repositories.transfer import TransferRepository
from app.services.repositories.user import UserRepository
from app.services.repositories.user_item import UserItemRepository


class StoreService:
    _user_repo: UserRepository
    _item_repo: ItemRepository
    _user_item_repo: UserItemRepository
    _transfer_repo: TransferRepository

    def __init__(
        self,
        item_repository: Annotated[ItemRepository, Depends()],
        user_repository: Annotated[UserRepository, Depends()],
        user_item_repository: Annotated[UserItemRepository, Depends()],
        transfer_repository: Annotated[TransferRepository, Depends()],
    ):
        self._user_repo = user_repository
        self._item_repo = item_repository
        self._user_item_repo = user_item_repository
        self._transfer_repo = transfer_repository

    async def get_user(self, username: str) -> User | None:
        return await self._user_repo.get(name=username, lock=True)

    async def auth_user(self, username: str, password: str):
        user = await self._user_repo.get(name=username)
        password = sha256(password.encode()).digest()
        password = b64encode(password)
        if user and not checkpw(password, user.hashed_password.encode()):
            raise UnauthorizedException(f"Bad password for user <{username}>")
        if not user:
            pwd_hash = hashpw(password, gensalt()).decode()
            await self._user_repo.add(username, pwd_hash)

    async def buy_item(self, user: User, item_type: str):
        item = await self._item_repo.get(type=item_type)
        if not item:
            raise BadRequestException(f"Item <{item_type}> doesn't exist")
        if user.coins < item.price:
            raise BadRequestException(
                f"User <{user.name}> doesn't have enough coins to buy <{item_type}>"
            )

        user_item = await self._user_item_repo.get(user_id=user.id, item_id=item.id)
        if not user_item:
            await self._user_item_repo.add(user.id, item.id)
        else:
            await self._user_item_repo.update_qty(user_item.id, user_item.quantity + 1)

        await self._user_repo.update_coins(user.id, user.coins - item.price)

    async def send_coin(self, from_user: User, to_username: str, amount: int):
        if from_user.coins < amount:
            raise BadRequestException(
                f"User <{from_user.name}> doesn't have enough coins to send <{to_username}>"
            )

        to_user = await self._user_repo.get(name=to_username, lock=True)
        if not to_user:
            raise BadRequestException(f"User <{to_username}> doesn't exist")

        if amount == 0 or from_user.name == to_username:
            return

        await self._transfer_repo.add(from_user.id, to_user.id, amount)
        await self._user_repo.update_coins(from_user.id, from_user.coins - amount)
        await self._user_repo.update_coins(to_user.id, to_user.coins + amount)

    async def get_user_info(self, user: User) -> dict[str, Any]:
        inventory = await self._user_item_repo.get_inventory(user.id)
        received = await self._transfer_repo.get_received(user.id)
        sent = await self._transfer_repo.get_sent(user.id)

        return {
            "name": user.name,
            "coins": user.coins,
            "inventory": inventory,
            "received": received,
            "sent": sent,
        }
