from app.db import Base

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    coins: Mapped[int] = mapped_column(default=1000)

    __table_args__ = (CheckConstraint("coins >= 0"),)


class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(unique=True)
    price: Mapped[int] 
    
    __table_args__ = (CheckConstraint("price >= 0"),)

