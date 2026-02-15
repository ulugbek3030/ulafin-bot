"""Transaction model — expenses and incomes."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("type IN ('expense', 'income')", name="ck_transaction_type"),
        Index("ix_transaction_user_created", "user_id", "created_at"),
        Index("ix_transaction_user_type_created", "user_id", "type", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    family_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("families.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(10), nullable=False, server_default="expense")
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="UZS")
    amount_base: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[str] = mapped_column(String(500), server_default="")
    source: Mapped[str] = mapped_column(String(20), server_default="text")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="transactions")  # noqa: F821
    category: Mapped["Category | None"] = relationship(lazy="joined")  # noqa: F821
    family: Mapped["Family | None"] = relationship()  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<Transaction id={self.id} {self.type} {self.amount} {self.currency}"
            f" user={self.user_id}>"
        )
