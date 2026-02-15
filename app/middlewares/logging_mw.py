"""Logging middleware — structured logging for every event."""

from __future__ import annotations

import time
from typing import Any, Awaitable, Callable

import structlog
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

log = structlog.get_logger()


class LoggingMiddleware(BaseMiddleware):
    """Log every incoming message/callback with timing."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        start = time.perf_counter()

        user_id = None
        event_type = type(event).__name__

        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            log.info(
                "message_received",
                user_id=user_id,
                text=event.text[:50] if event.text else "(no text)",
                chat_id=event.chat.id,
            )
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
            log.info(
                "callback_received",
                user_id=user_id,
                data=event.data,
            )

        try:
            result = await handler(event, data)
            elapsed = time.perf_counter() - start
            log.info(
                "event_handled",
                event_type=event_type,
                user_id=user_id,
                elapsed_ms=round(elapsed * 1000, 1),
            )
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            log.error(
                "event_error",
                event_type=event_type,
                user_id=user_id,
                error=str(e),
                elapsed_ms=round(elapsed * 1000, 1),
                exc_info=True,
            )
            raise
