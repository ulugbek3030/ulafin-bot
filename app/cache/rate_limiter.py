"""Redis-based rate limiter for Telegram handlers."""

from __future__ import annotations

import redis.asyncio as redis


class RateLimiter:
    """Sliding window rate limiter using Redis.

    Usage::

        limiter = RateLimiter(redis_client)
        allowed = await limiter.is_allowed(user_id=123, limit=30, window=60)
    """

    PREFIX = "rl:"

    def __init__(self, redis_client: redis.Redis) -> None:
        self._r = redis_client

    async def is_allowed(
        self,
        user_id: int,
        limit: int = 30,
        window: int = 60,
    ) -> bool:
        """Check if user is within rate limit.

        Args:
            user_id: Telegram user ID.
            limit: Max requests per window.
            window: Window size in seconds.

        Returns:
            True if allowed, False if rate-limited.
        """
        key = f"{self.PREFIX}{user_id}"
        current = await self._r.incr(key)
        if current == 1:
            await self._r.expire(key, window)
        return current <= limit

    async def get_remaining(self, user_id: int, limit: int = 30) -> int:
        """Get remaining requests for user."""
        key = f"{self.PREFIX}{user_id}"
        current = await self._r.get(key)
        used = int(current) if current else 0
        return max(0, limit - used)
