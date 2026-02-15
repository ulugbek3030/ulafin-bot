"""Migrate data from old SQLite database to new PostgreSQL.

Usage:
    python -m scripts.migrate_sqlite_to_pg /path/to/old/expenses.db <telegram_user_id>
"""

from __future__ import annotations

import asyncio
import sys
from decimal import Decimal

import aiosqlite
from sqlalchemy import select

from app.db.session import get_session
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User


async def migrate(sqlite_path: str, telegram_id: int) -> None:
    """Read old SQLite data and insert into PostgreSQL."""

    # 1. Ensure user exists
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_id=telegram_id, first_name="Migrated User")
            session.add(user)
            await session.commit()
            await session.refresh(user)
        user_id = user.id

    # 2. Read old custom categories
    async with aiosqlite.connect(sqlite_path) as old_db:
        cursor = await old_db.execute("SELECT key, label FROM custom_categories")
        old_categories = await cursor.fetchall()

    # 3. Insert custom categories
    async with get_session() as session:
        for key, label in old_categories:
            exists = await session.execute(
                select(Category).where(
                    Category.key == key, Category.user_id == user_id
                )
            )
            if exists.scalar_one_or_none() is None:
                icon = label.split()[0] if label else "📌"
                session.add(
                    Category(
                        key=key,
                        label=label,
                        icon=icon,
                        is_default=False,
                        user_id=user_id,
                    )
                )
        await session.commit()

    # 4. Build category key → id mapping
    async with get_session() as session:
        result = await session.execute(select(Category))
        all_cats = result.scalars().all()
        cat_map: dict[str, int] = {c.key: c.id for c in all_cats}

    # 5. Read old expenses
    async with aiosqlite.connect(sqlite_path) as old_db:
        old_db.row_factory = aiosqlite.Row
        cursor = await old_db.execute(
            "SELECT amount, category, description, source, type, created_at FROM expenses"
        )
        old_expenses = await cursor.fetchall()

    # 6. Insert transactions
    async with get_session() as session:
        count = 0
        for row in old_expenses:
            category_id = cat_map.get(row["category"])
            session.add(
                Transaction(
                    user_id=user_id,
                    type=row["type"] or "expense",
                    amount=Decimal(str(row["amount"])),
                    currency="UZS",
                    amount_base=Decimal(str(row["amount"])),
                    category_id=category_id,
                    description=row["description"] or "",
                    source=row["source"] or "text",
                )
            )
            count += 1
        await session.commit()

    print(f"✅ Migrated {count} transactions and {len(old_categories)} custom categories")
    print(f"   User: telegram_id={telegram_id}, db_id={user_id}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m scripts.migrate_sqlite_to_pg <sqlite_path> <telegram_user_id>")
        sys.exit(1)

    sqlite_path = sys.argv[1]
    telegram_id = int(sys.argv[2])
    asyncio.run(migrate(sqlite_path, telegram_id))
