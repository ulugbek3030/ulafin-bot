"""Registration gate middleware — blocks unregistered users from using the bot.

Only /start and contact sharing are allowed for unregistered users.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.models.user import User


class RegistrationMiddleware(BaseMiddleware):
    """Block unregistered users from features — only /start and contact allowed."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("user")

        if user is None or user.is_registered:
            return await handler(event, data)

        # Allow /start and contact messages for unregistered users
        if isinstance(event, Message):
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)
            if event.contact:
                return await handler(event, data)
            if event.text and event.text.startswith("/help"):
                return await handler(event, data)
            # Block everything else
            await event.answer(
                "Для начала пройди регистрацию — нажми /start"
            )
            return None

        if isinstance(event, CallbackQuery):
            await event.answer(
                "Сначала пройди регистрацию — нажми /start",
                show_alert=True,
            )
            return None

        return await handler(event, data)
