"""Currency and exchange rate models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    decimal_places: Mapped[int] = mapped_column(Integer, server_default="2")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"<Currency {self.code} ({self.symbol})>"


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    from_currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    source: Mapped[str] = mapped_column(String(50), server_default="cbu.uz")
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"<ExchangeRate {self.from_currency}→{self.to_currency} = {self.rate}>"
