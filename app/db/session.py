"""Session helpers — context manager and dependency for handlers."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import async_session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope around a series of operations.

    Usage::

        async with get_session() as session:
            session.add(obj)
            await session.commit()
    """
    session = async_session_factory()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
