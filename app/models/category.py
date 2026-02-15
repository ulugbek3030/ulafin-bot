"""Category model — built-in (global) + user-created (per-user)."""

from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("user_id", "key", name="uq_category_user_key"),
    )

    key: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str] = mapped_column(String(10), server_default="📌")
    is_default: Mapped[bool] = mapped_column(Boolean, server_default="false")
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )

    # Relationships
    user: Mapped["User | None"] = relationship(back_populates="categories")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Category key={self.key!r} label={self.label!r} user_id={self.user_id}>"
