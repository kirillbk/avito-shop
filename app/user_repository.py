from app.db import get_db
from app.models import User

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated


class UserRepository:
    _session: AsyncSession

    def __init__(self, session: Annotated[AsyncSession, Depends(get_db)]):
        self._session = session

    async def get_user(self, user_id: int = None, name: str = None) -> User | None:
        if not user_id and not name:
            return None

        stmt = select(User)
        if user_id:
            stmt = stmt.where(User.id == user_id)
        if name:
            stmt = stmt.where(User.name == name)

        return await self._session.scalar(stmt)

    async def add_user(self, name: str, password: str) -> User | None:
        user = User(name=name, hashed_password=password)
        self._session.add(user)

        try:
            return await self._session.commit()
        except IntegrityError:
            return None
        else:
            return user
