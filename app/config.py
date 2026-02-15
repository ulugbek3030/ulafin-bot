"""Application configuration via Pydantic Settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app settings, loaded from .env / environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Telegram ──────────────────────────────────────────────
    bot_token: str

    # ── PostgreSQL ────────────────────────────────────────────
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "ulafin"
    postgres_password: str = "ulafin_secret"
    postgres_db: str = "ulafin"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync URL for Alembic migrations."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ── Redis ─────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── App ───────────────────────────────────────────────────
    app_env: Literal["development", "production", "testing"] = "development"
    log_level: str = "DEBUG"
    default_language: str = "ru"
    default_currency: str = "UZS"
    default_timezone: str = "Asia/Tashkent"

    # ── Sentry ────────────────────────────────────────────────
    sentry_dsn: str = ""

    # ── Webhook (production) ──────────────────────────────────
    webhook_url: str = ""
    webhook_secret: str = ""
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8443

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def use_webhook(self) -> bool:
        return self.is_production and bool(self.webhook_url)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton settings instance (cached)."""
    return Settings()  # type: ignore[call-arg]
