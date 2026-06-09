"""
Rate-limit middleware — не более одного сообщения в секунду на пользователя.
"""

from __future__ import annotations

import os
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from fastvk import FastVK
from fastvk.middleware import BaseMiddleware
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, rate: float = 1.0) -> None:
        self._rate = rate
        self._last: dict[int, float] = defaultdict(float)

    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        if isinstance(event, Message):
            now = time.monotonic()
            last = self._last[event.from_id]
            if now - last < self._rate:
                await event.answer("Не так быстро! Подожди секунду.")
                return None
            self._last[event.from_id] = now
        return await handler(event, data)


bot = FastVK(
    token=os.environ["VK_TOKEN"],
    group_id=int(os.environ["VK_GROUP_ID"]),
    middleware=[RateLimitMiddleware(rate=1.0)],
)


@bot.message()
async def echo(message: Message) -> None:
    await message.answer(message.text)


if __name__ == "__main__":
    bot.run_polling()
