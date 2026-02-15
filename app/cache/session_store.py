"""Redis-backed session store — replaces in-memory dicts from v1.

Stores:
- pending_expenses  (key: msg_id → expense data)
- waiting_new_category (key: user_id → expense data)
- current_mode (key: user_id → "expense" | "income")

All data is JSON-serialized and has TTL to auto-expire stale entries.
"""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as redis


class SessionStore:
    """Redis-backed store for transient user session data."""

    # TTL constants (seconds)
    PENDING_TTL = 3600  # 1 hour — pending category selection
    WAITING_TTL = 600  # 10 min — waiting for new category name
    MODE_TTL = 86400  # 24 hours — current input mode

    # Key prefixes
    PREFIX_PENDING = "pending:"  # pending:{msg_id}
    PREFIX_WAITING = "waiting:"  # waiting:{user_id}
    PREFIX_MODE = "mode:"  # mode:{user_id}

    def __init__(self, redis_client: redis.Redis) -> None:
        self._r = redis_client

    # ── Pending expenses (waiting for category pick) ──────────

    async def set_pending(self, msg_id: int, data: dict[str, Any]) -> None:
        key = f"{self.PREFIX_PENDING}{msg_id}"
        await self._r.set(key, json.dumps(data), ex=self.PENDING_TTL)

    async def get_pending(self, msg_id: int) -> dict[str, Any] | None:
        key = f"{self.PREFIX_PENDING}{msg_id}"
        raw = await self._r.get(key)
        return json.loads(raw) if raw else None

    async def pop_pending(self, msg_id: int) -> dict[str, Any] | None:
        key = f"{self.PREFIX_PENDING}{msg_id}"
        raw = await self._r.getdel(key)
        return json.loads(raw) if raw else None

    # ── Waiting for new category name ─────────────────────────

    async def set_waiting_category(self, user_id: int, data: dict[str, Any]) -> None:
        key = f"{self.PREFIX_WAITING}{user_id}"
        await self._r.set(key, json.dumps(data), ex=self.WAITING_TTL)

    async def get_waiting_category(self, user_id: int) -> dict[str, Any] | None:
        key = f"{self.PREFIX_WAITING}{user_id}"
        raw = await self._r.get(key)
        return json.loads(raw) if raw else None

    async def pop_waiting_category(self, user_id: int) -> dict[str, Any] | None:
        key = f"{self.PREFIX_WAITING}{user_id}"
        raw = await self._r.getdel(key)
        return json.loads(raw) if raw else None

    async def is_waiting_category(self, user_id: int) -> bool:
        key = f"{self.PREFIX_WAITING}{user_id}"
        return bool(await self._r.exists(key))

    # ── Current mode (expense / income) ───────────────────────

    async def set_mode(self, user_id: int, mode: str) -> None:
        key = f"{self.PREFIX_MODE}{user_id}"
        await self._r.set(key, mode, ex=self.MODE_TTL)

    async def get_mode(self, user_id: int) -> str:
        key = f"{self.PREFIX_MODE}{user_id}"
        raw = await self._r.get(key)
        return raw if raw else "expense"
