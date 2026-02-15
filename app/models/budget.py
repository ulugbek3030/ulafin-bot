"""Budget models — spending limits and alerts."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        CheckConstraint(
            "period IN ('weekly', 'monthly', 'yearly')", name="ck_budget_period"
        ),
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    family_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("families.id", ondelete="CASCADE"), nullable=True
    )
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    amount_limit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), server_default="UZS")
    period: Mapped[str] = mapped_column(String(10), server_default="monthly")
    alert_at_percent: Mapped[int] = mapped_column(Integer, server_default="80")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship()  # noqa: F821
    category: Mapped["Category | None"] = relationship()  # noqa: F821
    alerts: Mapped[list["BudgetAlert"]] = relationship(
        back_populates="budget", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<Budget id={self.id} user={self.user_id}"
            f" limit={self.amount_limit} {self.period}>"
        )


class BudgetAlert(Base):
    __tablename__ = "budget_alerts"

    budget_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False
    )
    percent_reached: Mapped[int] = mapped_column(Integer, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    budget: Mapped["Budget"] = relationship(back_populates="alerts")

    def __repr__(self) -> str:
        return f"<BudgetAlert budget={self.budget_id} reached={self.percent_reached}%>"
