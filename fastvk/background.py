from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("fastvk.background")


class BackgroundTasks:
    """
    Run tasks after the handler returns — identical API to FastAPI's BackgroundTasks.

    ```python
    async def notify(user_id: int) -> None:
        await asyncio.sleep(1)
        print(f"notify {user_id}")

    @router.message()
    async def handler(message: Message, background: BackgroundTasks) -> None:
        background.add_task(notify, message.from_id)
        await message.answer("OK")  # reply sent, notify runs after
    ```
    """

    def __init__(self) -> None:
        self._tasks: list[tuple[Callable[..., Any], tuple[Any, ...], dict[str, Any]]] = []

    def add_task(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Schedule *func* to run after the handler completes."""
        self._tasks.append((func, args, kwargs))

    async def _run(self) -> None:
        for func, args, kwargs in self._tasks:
            try:
                result = func(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                logger.exception("Background task %r raised an exception", func.__name__)
