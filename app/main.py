"""UlaFin Bot — entry point.

Supports both long-polling (dev) and webhook (prod) modes.
"""

from __future__ import annotations

import asyncio
import logging
import sys

import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.cache.rate_limiter import RateLimiter
from app.cache.redis_client import close_redis, get_redis
from app.cache.session_store import SessionStore
from app.config import get_settings
from app.db.engine import engine
from app.handlers import register_all_routers
from app.middlewares.auth import AuthMiddleware
from app.middlewares.db_session import DbSessionMiddleware
from app.middlewares.logging_mw import LoggingMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware
from app.middlewares.registration import RegistrationMiddleware


def setup_logging(log_level: str) -> None:
    """Configure structlog + stdlib logging."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer()
            if not get_settings().is_production
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def _run_alembic_upgrade(connection, alembic_cfg) -> None:
    """Synchronous helper to run Alembic migrations within run_sync()."""
    from alembic import command

    alembic_cfg.attributes["connection"] = connection
    command.upgrade(alembic_cfg, "head")


async def on_startup(bot: Bot) -> None:
    """Run on bot startup — initialize DB, Redis, run migrations."""
    log = structlog.get_logger()

    # Initialize Redis
    redis = await get_redis()
    await redis.ping()
    log.info("redis_connected")

    # Verify database connection
    async with engine.begin() as conn:
        await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    log.info("database_connected")

    # Run Alembic migrations (async-safe — avoids nested asyncio.run)
    log.info("running_migrations")
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")

    # Run migrations using an existing async connection passed into env.py
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: _run_alembic_upgrade(sync_conn, alembic_cfg)
        )
    log.info("migrations_complete")

    # Seed default categories if empty
    from scripts.seed_categories import seed as seed_categories
    from scripts.seed_currencies import seed as seed_currencies

    await seed_categories()
    await seed_currencies()

    me = await bot.get_me()
    log.info("bot_started", username=me.username, bot_id=me.id)


async def on_shutdown(bot: Bot) -> None:
    """Clean up on shutdown."""
    log = structlog.get_logger()
    await close_redis()
    await engine.dispose()
    log.info("bot_stopped")


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    log = structlog.get_logger()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # ── Initialize Redis services ─────────────────────────────
    redis = await get_redis()
    session_store = SessionStore(redis)
    rate_limiter = RateLimiter(redis)

    # ── Register middlewares (order: outer → inner) ───────────
    # Logging → Rate limit → Auth → DB Session
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    dp.message.middleware(RateLimitMiddleware(rate_limiter))
    dp.callback_query.middleware(RateLimitMiddleware(rate_limiter))

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())

    dp.message.middleware(RegistrationMiddleware())
    dp.callback_query.middleware(RegistrationMiddleware())

    # ── Inject session_store into all handlers ────────────────
    dp["session_store"] = session_store

    # ── Register routers ──────────────────────────────────────
    register_all_routers(dp)

    if settings.use_webhook:
        log.info("starting_webhook", url=settings.webhook_url)
        from aiohttp import web
        from aiogram.webhook.aiohttp_server import (
            SimpleRequestHandler,
            setup_application,
        )

        await bot.set_webhook(
            url=settings.webhook_url,
            secret_token=settings.webhook_secret,
        )
        app = web.Application()
        handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        handler.register(app, path="/webhook")
        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, settings.webhook_host, settings.webhook_port)
        await site.start()
        log.info(
            "webhook_running", host=settings.webhook_host, port=settings.webhook_port
        )

        # Keep running
        await asyncio.Event().wait()
    else:
        log.info("starting_polling")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
