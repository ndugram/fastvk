"""
Middleware для логирования всех входящих апдейтов.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Awaitable, Callable
from typing import Any

from fastvk import FastVK
from fastvk.filters import Command
from fastvk.middleware import BaseMiddleware
from fastvk.types import Message, Update

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("fastvk.example")


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        start = time.monotonic()
        update: Update | None = data.get(Update)
        event_type = update.type if update else type(event).__name__
        logger.info("→ %s", event_type)
        result = await handler(event, data)
        logger.info("← %s  %.3f сек", event_type, time.monotonic() - start)
        return result


class UserAgentMiddleware(BaseMiddleware):
    """Добавляет информацию о пользователе в data."""

    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        if isinstance(event, Message):
            logger.debug("from_id=%d peer_id=%d", event.from_id, event.peer_id)
        return await handler(event, data)


bot = FastVK(
    token=os.environ["VK_TOKEN"],
    group_id=int(os.environ["VK_GROUP_ID"]),
    middleware=[LoggingMiddleware(), UserAgentMiddleware()],
)


@bot.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("pong")


@bot.message()
async def echo(message: Message) -> None:
    await message.answer(message.text)


if __name__ == "__main__":
    bot.run_polling()
