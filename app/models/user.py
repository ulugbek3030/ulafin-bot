"""User model — one row per Telegram user."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    is_registered: Mapped[bool] = mapped_column(Boolean, server_default="false")
    language: Mapped[str] = mapped_column(String(5), server_default="ru")
    default_currency: Mapped[str] = mapped_column(String(3), server_default="UZS")
    timezone: Mapped[str] = mapped_column(String(50), server_default="Asia/Tashkent")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        back_populates="user", lazy="selectin"
    )
    categories: Mapped[list["Category"]] = relationship(  # noqa: F821
        back_populates="user", lazy="selectin"
    )
    reminders: Mapped[list["Reminder"]] = relationship(  # noqa: F821
        back_populates="user", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} tg={self.telegram_id} name={self.first_name!r}>"
