"""Base repository with common CRUD operations."""

from __future__ import annotations

from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic CRUD repository for SQLAlchemy models."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id_: int) -> ModelT | None:
        return await self._session.get(self.model, id_)

    async def get_all(self, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs: Any) -> ModelT:
        obj = self.model(**kwargs)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update_by_id(self, id_: int, **kwargs: Any) -> None:
        stmt = update(self.model).where(self.model.id == id_).values(**kwargs)
        await self._session.execute(stmt)

    async def delete_by_id(self, id_: int) -> bool:
        stmt = delete(self.model).where(self.model.id == id_)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def count(self) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        result = await self._session.execute(stmt)
        return result.scalar_one()
