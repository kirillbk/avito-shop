from app.db.base_repository import BaseRepository
from app.db.models import UserItem

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError


class UserItemRepository(BaseRepository):
    async def get_item(
        self, id: int = None, user_id: int = None, item_id=None
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

    async def add_item(self, user_id: int, item_id: int) -> UserItem | None:
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
