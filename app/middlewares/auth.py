"""Auth middleware — auto-registration of Telegram users.

Every incoming message/callback triggers get_or_create for the user.
The User object is injected into handler data as `user`.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.db.session import get_session
from app.services.user_service import UserService


class AuthMiddleware(BaseMiddleware):
    """Auto-register users and inject User object into handler data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_obj = None

        if isinstance(event, Message) and event.from_user:
            tg_user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            tg_user = event.from_user
        else:
            return await handler(event, data)

        async with get_session() as session:
            service = UserService(session)
            user_obj = await service.get_or_create(
                telegram_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
            )

        data["user"] = user_obj
        return await handler(event, data)
