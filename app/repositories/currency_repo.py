"""Currency repository — currencies and exchange rates."""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from sqlalchemy import select

from app.models.currency import Currency, ExchangeRate
from app.repositories.base import BaseRepository


class CurrencyRepository(BaseRepository[Currency]):
    model = Currency

    async def get_by_code(self, code: str) -> Currency | None:
        stmt = select(Currency).where(Currency.code == code)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_codes(self) -> list[str]:
        stmt = select(Currency.code).order_by(Currency.code)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class ExchangeRateRepository(BaseRepository[ExchangeRate]):
    model = ExchangeRate

    async def get_rate(self, from_code: str, to_code: str) -> Decimal | None:
        """Get latest exchange rate between two currencies."""
        stmt = (
            select(ExchangeRate.rate)
            .where(
                ExchangeRate.from_currency == from_code,
                ExchangeRate.to_currency == to_code,
            )
            .order_by(ExchangeRate.fetched_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_rate(
        self,
        from_code: str,
        to_code: str,
        rate: Decimal,
        source: str = "cbu.uz",
    ) -> ExchangeRate:
        """Insert a new exchange rate record."""
        return await self.create(
            from_currency=from_code,
            to_currency=to_code,
            rate=rate,
            source=source,
        )

    async def get_all_latest(self) -> Sequence[ExchangeRate]:
        """Get latest rate for each currency pair."""
        # Simple approach: get all, app will deduplicate
        stmt = select(ExchangeRate).order_by(ExchangeRate.fetched_at.desc()).limit(50)
        result = await self._session.execute(stmt)
        return result.scalars().all()
