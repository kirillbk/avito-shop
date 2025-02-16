from app.db.base_repository import BaseRepository
from app.db.models import User

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError


class UserRepository(BaseRepository):
    async def get(
        self, id: int = None, name: str = None, lock: bool = False
    ) -> User | None:
        if not (id or name):
            return None

        stmt = select(User)
        if id:
            stmt = stmt.where(User.id == id)
        if name:
            stmt = stmt.where(User.name == name)
        if lock:
            stmt = stmt.with_for_update(key_share=True)

        return await self._session.scalar(stmt)

    async def add(self, name: str, password: str) -> User | None:
        user = User(name=name, hashed_password=password)
        self._session.add(user)

        try:
            await self._session.commit()
        except IntegrityError:
            return None
        else:
            return user

    async def update_coins(self, id: int, qty: int):
        stmt = update(User).where(User.id == id).values(coins=qty)

        await self._session.execute(stmt)
        await self._session.commit()
