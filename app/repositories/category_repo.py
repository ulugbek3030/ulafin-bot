"""Category repository — database operations for categories."""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import or_, select

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    model = Category

    async def get_for_user(self, user_id: int) -> Sequence[Category]:
        """Get all categories available to a user (defaults + user-created)."""
        stmt = (
            select(Category)
            .where(
                or_(
                    Category.is_default.is_(True),
                    Category.user_id == user_id,
                )
            )
            .order_by(Category.is_default.desc(), Category.key)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_key(self, key: str, user_id: int | None = None) -> Category | None:
        """Get category by key — checks user-specific first, then defaults."""
        if user_id:
            stmt = select(Category).where(
                Category.key == key, Category.user_id == user_id
            )
            result = await self._session.execute(stmt)
            cat = result.scalar_one_or_none()
            if cat:
                return cat

        # Fall back to default
        stmt = select(Category).where(
            Category.key == key, Category.is_default.is_(True)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_custom(
        self,
        user_id: int,
        key: str,
        label: str,
        icon: str = "📌",
    ) -> Category:
        """Create a custom category for a specific user."""
        return await self.create(
            key=key,
            label=label,
            icon=icon,
            is_default=False,
            user_id=user_id,
        )

    async def get_defaults(self) -> Sequence[Category]:
        """Get only default (global) categories."""
        stmt = (
            select(Category)
            .where(Category.is_default.is_(True))
            .order_by(Category.key)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
