from sqlalchemy import select

from app.db.base_repository import BaseRepository
from app.db.models import Item


class ItemRepository(BaseRepository):
    async def get(self, id: int | None = None, type: str | None = None) -> Item | None:
        if not (id or type):
            return None

        stmt = select(Item)
        if id:
            stmt = stmt.where(Item.id == id)
        if type:
            stmt = stmt.where(Item.type == type)

        return await self._session.scalar(stmt)
