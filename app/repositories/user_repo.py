"""User repository — database operations for users."""

from __future__ import annotations

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> User:
        """Get existing user or create new one (auto-registration)."""
        user = await self.get_by_telegram_id(telegram_id)
        if user is not None:
            # Update username/name if changed
            changed = False
            if username and user.username != username:
                user.username = username
                changed = True
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                changed = True
            if changed:
                await self._session.flush()
            return user

        # Create new user
        return await self.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
        )

    async def update_settings(
        self,
        user_id: int,
        language: str | None = None,
        default_currency: str | None = None,
        timezone: str | None = None,
    ) -> None:
        kwargs = {}
        if language is not None:
            kwargs["language"] = language
        if default_currency is not None:
            kwargs["default_currency"] = default_currency
        if timezone is not None:
            kwargs["timezone"] = timezone
        if kwargs:
            await self.update_by_id(user_id, **kwargs)
