from collections.abc import Sequence

from sqlalchemy import RowMapping, select

from app.db.base_repository import BaseRepository
from app.db.models import Transfer, User


class TransferRepository(BaseRepository):
    async def add(self, from_id: int, to_id: int, amount: int) -> Transfer:
        transfer = Transfer(from_user_id=from_id, to_user_id=to_id, amount=amount)

        self._session.add(transfer)

        await self._session.commit()

    async def get_received(self, user_id: int) -> Sequence[RowMapping]:
        stmt = select(User.name, Transfer.amount)
        stmt = stmt.join(User, Transfer.from_user_id == User.id)
        stmt = stmt.where(Transfer.to_user_id == user_id)

        res = await self._session.execute(stmt)
        return res.mappings().all()

    async def get_sent(self, user_id: int) -> Sequence[RowMapping]:
        stmt = select(User.name, Transfer.amount)
        stmt = stmt.join(User, Transfer.to_user_id == User.id)
        stmt = stmt.where(Transfer.from_user_id == user_id)

        res = await self._session.execute(stmt)
        return res.mappings().all()
