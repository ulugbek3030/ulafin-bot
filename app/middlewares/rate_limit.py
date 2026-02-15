"""Rate limiting middleware — Redis-based per-user throttling."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.cache.rate_limiter import RateLimiter


class RateLimitMiddleware(BaseMiddleware):
    """Throttle users who send too many messages."""

    def __init__(self, limiter: RateLimiter, limit: int = 30, window: int = 60) -> None:
        self._limiter = limiter
        self._limit = limit
        self._window = window

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id: int | None = None

        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id is not None:
            allowed = await self._limiter.is_allowed(
                user_id, self._limit, self._window
            )
            if not allowed:
                if isinstance(event, Message):
                    await event.answer(
                        "⏳ Слишком много запросов. Подождите немного."
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "⏳ Подождите немного.", show_alert=True
                    )
                return None

        return await handler(event, data)
