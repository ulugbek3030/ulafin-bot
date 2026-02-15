"""Global error handler — catches all unhandled exceptions."""

from __future__ import annotations

import structlog
from aiogram import Router
from aiogram.types import ErrorEvent

log = structlog.get_logger()

router = Router()


@router.errors()
async def global_error_handler(event: ErrorEvent) -> bool:
    """Catch-all error handler — log and notify user."""
    import traceback

    print(f"[ERROR] {event.exception}", flush=True)
    traceback.print_exception(
        type(event.exception), event.exception, event.exception.__traceback__
    )
    log.error(
        "unhandled_error",
        error=str(event.exception),
        exc_info=event.exception,
    )

    # Try to notify the user
    update = event.update
    if update.message:
        try:
            await update.message.answer(
                "⚠️ Произошла ошибка. Попробуйте ещё раз или напишите /start"
            )
        except Exception:
            pass
    elif update.callback_query:
        try:
            await update.callback_query.answer(
                "⚠️ Произошла ошибка. Попробуйте ещё раз.",
                show_alert=True,
            )
        except Exception:
            pass

    return True  # Mark as handled
