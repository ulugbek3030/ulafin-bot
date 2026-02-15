"""Reminder model — daily/weekly expense tracking nudges."""

from __future__ import annotations

from datetime import datetime, time

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (
        CheckConstraint(
            "type IN ('daily', 'weekly')", name="ck_reminder_type"
        ),
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(10), nullable=False, server_default="daily")
    time: Mapped[time] = mapped_column(Time, nullable=False)
    day_of_week: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # 0=Mon, 6=Sun (for weekly)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    last_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="reminders")  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<Reminder id={self.id} user={self.user_id}"
            f" {self.type} at {self.time} active={self.is_active}>"
        )
