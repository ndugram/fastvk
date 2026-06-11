from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from .base import BaseMiddleware


class ThrottlingMiddleware(BaseMiddleware):
    """
    Silently drops repeated updates from the same user faster than *rate* seconds apart.

    Registered automatically by :class:`~fastvk.FastVK` — no manual setup needed.
    Disable by passing ``throttle_rate=0`` to :class:`~fastvk.FastVK`.
    """

    def __init__(self, rate: float = 1.0) -> None:
        self._rate = rate
        self._last: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        user_id = self._user_id(event)
        if user_id is not None and user_id > 0:
            now = time.monotonic()
            if now - self._last.get(user_id, 0.0) < self._rate:
                return None
            self._last[user_id] = now
        return await handler(event, data)

    @staticmethod
    def _user_id(event: Any) -> int | None:
        from ..types.update import Update
        if not isinstance(event, Update):
            return None
        obj = event.object
        return (
            obj.get("message", {}).get("from_id")
            or obj.get("user_id")
            or obj.get("from_id")
        )
