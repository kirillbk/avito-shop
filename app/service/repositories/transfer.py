from app.db.base_repository import BaseRepository
from app.db.models import Transfer

from sqlalchemy import select


class TransferRepository(BaseRepository):
    async def add(self, from_id: int, to_id: int, amount: int) -> Transfer:
        transfer = Transfer(from_user_id=from_id, to_user_id=to_id, amount=amount)
        self._session.add(transfer)

        await self._session.commit()
