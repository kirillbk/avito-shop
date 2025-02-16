from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


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


class UserItem(Base):
    __tablename__ = "user_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"))
    quantity: Mapped[int] = mapped_column(default=1)

    __table_args__ = (
        CheckConstraint("quantity > 0"),
        UniqueConstraint("user_id", "item_id"),
    )
