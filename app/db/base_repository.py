from app.db.db import get_db

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from abc import ABC
from typing import Annotated


class BaseRepository(ABC):
    _session: AsyncSession

    def __init__(self, session: Annotated[AsyncSession, Depends(get_db)]):
        self._session = session