"""User service — business logic for user management."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repo import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)
        self._session = session

    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> User:
        """Get existing user or auto-register a new one."""
        user = await self._repo.upsert(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
        )
        await self._session.commit()
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        return await self._repo.get_by_telegram_id(telegram_id)

    async def update_language(self, user_id: int, language: str) -> None:
        await self._repo.update_settings(user_id, language=language)
        await self._session.commit()

    async def update_currency(self, user_id: int, currency: str) -> None:
        await self._repo.update_settings(user_id, default_currency=currency)
        await self._session.commit()

    async def update_timezone(self, user_id: int, timezone: str) -> None:
        await self._repo.update_settings(user_id, timezone=timezone)
        await self._session.commit()

    async def complete_registration(self, user_id: int, phone: str) -> None:
        """Save phone number and mark user as registered."""
        await self._repo.update_by_id(user_id, phone=phone, is_registered=True)
        await self._session.commit()
