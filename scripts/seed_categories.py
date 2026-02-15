"""Seed default categories into the database."""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.db.session import get_session
from app.models.category import Category

DEFAULT_CATEGORIES = [
    ("food", "🍔 Еда", "🍔"),
    ("cafe", "☕ Кафе/Ресторан", "☕"),
    ("grocery", "🛒 Продукты", "🛒"),
    ("transport", "🚕 Транспорт", "🚕"),
    ("housing", "🏠 Жильё", "🏠"),
    ("utilities", "💡 Коммуналка", "💡"),
    ("entertainment", "🎮 Развлечения", "🎮"),
    ("clothes", "👕 Одежда", "👕"),
    ("health", "💊 Здоровье", "💊"),
    ("fitness", "💪 Спорт/Фитнес", "💪"),
    ("telecom", "📱 Связь/Интернет", "📱"),
    ("education", "📚 Образование", "📚"),
    ("gifts", "🎁 Подарки", "🎁"),
    ("travel", "✈️ Путешествия", "✈️"),
    ("beauty", "💅 Красота", "💅"),
    ("pets", "🐾 Питомцы", "🐾"),
    ("tech", "💻 Техника", "💻"),
    ("subscriptions", "📺 Подписки", "📺"),
    ("other", "📦 Другое", "📦"),
]


async def seed() -> None:
    async with get_session() as session:
        for key, label, icon in DEFAULT_CATEGORIES:
            exists = await session.execute(
                select(Category).where(
                    Category.key == key,
                    Category.is_default.is_(True),
                    Category.user_id.is_(None),
                )
            )
            if exists.scalar_one_or_none() is None:
                session.add(
                    Category(
                        key=key,
                        label=label,
                        icon=icon,
                        is_default=True,
                        user_id=None,
                    )
                )
        await session.commit()
    print(f"✅ Seeded {len(DEFAULT_CATEGORIES)} default categories")


if __name__ == "__main__":
    asyncio.run(seed())
