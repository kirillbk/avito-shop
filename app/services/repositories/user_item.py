from collections.abc import Sequence

from sqlalchemy import RowMapping, select, update
from sqlalchemy.exc import IntegrityError

from app.db.base_repository import BaseRepository
from app.db.models import Item, UserItem


class UserItemRepository(BaseRepository):
    async def get(
        self, id: int | None = None, user_id: int | None = None, item_id=None
    ) -> UserItem | None:
        if not (id or user_id or item_id):
            return None

        stmt = select(UserItem)
        if id:
            stmt = stmt.where(UserItem.id == id)
        if user_id:
            stmt = stmt.where(UserItem.user_id == user_id)
        if item_id:
            stmt = stmt.where(UserItem.item_id == item_id)

        return await self._session.scalar(stmt)

    async def add(self, user_id: int, item_id: int) -> UserItem | None:
        item = UserItem(user_id=user_id, item_id=item_id)
        self._session.add(item)

        try:
            await self._session.commit()
        except IntegrityError:
            return None
        else:
            return item

    async def update_qty(self, id: int, qty: int):
        stmt = update(UserItem).where(UserItem.id == id).values(quantity=qty)

        await self._session.execute(stmt)
        await self._session.commit()

    async def get_inventory(self, user_id: int) -> Sequence[RowMapping]:
        stmt = select(Item.type, UserItem.quantity).join(Item)
        stmt = stmt.where(UserItem.user_id == user_id)

        res = await self._session.execute(stmt)
        return res.mappings().all()
