"""Seed supported currencies into the database."""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.db.session import get_session
from app.models.currency import Currency

CURRENCIES = [
    ("UZS", "Узбекский сум", "сум", 0),
    ("USD", "Доллар США", "$", 2),
    ("EUR", "Евро", "€", 2),
    ("RUB", "Российский рубль", "₽", 2),
    ("GBP", "Фунт стерлингов", "£", 2),
    ("KZT", "Казахский тенге", "₸", 0),
]


async def seed() -> None:
    async with get_session() as session:
        for code, name, symbol, decimals in CURRENCIES:
            exists = await session.execute(
                select(Currency).where(Currency.code == code)
            )
            if exists.scalar_one_or_none() is None:
                session.add(
                    Currency(
                        code=code,
                        name=name,
                        symbol=symbol,
                        decimal_places=decimals,
                    )
                )
        await session.commit()
    print(f"✅ Seeded {len(CURRENCIES)} currencies")


if __name__ == "__main__":
    asyncio.run(seed())
