"""Category service — business logic for categories."""

from __future__ import annotations

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repo import CategoryRepository
from app.utils.icons import pick_icon


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = CategoryRepository(session)
        self._session = session

    async def get_for_user(self, user_id: int) -> Sequence[Category]:
        """Get all categories available to a user (defaults + custom)."""
        return await self._repo.get_for_user(user_id)

    async def get_by_id(self, category_id: int) -> Category | None:
        return await self._repo.get_by_id(category_id)

    async def get_by_key(self, key: str, user_id: int | None = None) -> Category | None:
        return await self._repo.get_by_key(key, user_id)

    async def create_custom(
        self,
        user_id: int,
        name: str,
    ) -> Category:
        """Create a new custom category with auto-detected icon.

        Args:
            user_id: Owner user ID.
            name: Category display name (e.g., "Продукты", "Спорт").

        Returns:
            Created category.
        """
        icon = pick_icon(name)
        key = name.lower().replace(" ", "_")
        label = f"{icon} {name}"

        category = await self._repo.create_custom(
            user_id=user_id,
            key=key,
            label=label,
            icon=icon,
        )
        await self._session.commit()
        return category

    async def get_defaults(self) -> Sequence[Category]:
        return await self._repo.get_defaults()
