"""Handler registration — order matters!

Router order:
1. errors  — global error handler
2. start   — /start, /help, mode buttons (exact text matches)
3. settings — settings callbacks
4. categories — category selection + new category (callbacks + waiting state)
5. reports  — /report + report type callbacks
6. add_transaction — text + photo (catch-all, must be LAST)
"""

from __future__ import annotations

from aiogram import Dispatcher

from app.handlers import (
    add_transaction,
    categories,
    errors,
    reports,
    settings,
    start,
)


def register_all_routers(dp: Dispatcher) -> None:
    """Register all routers in the correct order."""
    dp.include_router(errors.router)
    dp.include_router(start.router)
    dp.include_router(settings.router)
    dp.include_router(categories.router)
    dp.include_router(reports.router)
    dp.include_router(add_transaction.router)  # Must be last (catch-all F.text)
