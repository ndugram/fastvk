from __future__ import annotations

import asyncio
import logging
from typing import Annotated, TYPE_CHECKING

from annotated_doc import Doc

from .api.client import Bot
from .fsm.storage import BaseStorage, MemoryStorage
from .middleware.base import BaseMiddleware, MiddlewareManager
from .polling.longpoll import LongPoller
from .router import Router
from .types.update import Update

if TYPE_CHECKING:
    pass

logger = logging.getLogger("fastvk")


class FastVK(Router):
    """
    FastVK application — the root dispatcher and entry point.

    Extends :class:`~fastvk.Router`, so you can register handlers
    directly on the bot instance or via ``include_router()``.

    ```python
    from fastvk import FastVK, Router
    from fastvk.filters import Command
    from fastvk.types import Message

    bot = FastVK(token="vk1.a...", group_id=123456789)

    @bot.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer("Привет!")

    if __name__ == "__main__":
        bot.run_polling()
    ```
    """

    def __init__(
        self,
        token: Annotated[
            str,
            Doc(
                """
                VK community token with the required permissions.

                Obtain in community settings → Manage → API usage → Access tokens.
                The token must have at least the ``messages`` permission.
                """
            ),
        ],
        group_id: Annotated[
            int,
            Doc(
                """
                Numeric ID of the VK community.

                Shown in the community URL: ``vk.com/public{group_id}``
                or retrievable via ``groups.getById``.
                """
            ),
        ],
        *,
        api_version: Annotated[
            str,
            Doc(
                """
                VK API version used for all requests.

                FastVK is tested against 5.199. Avoid downgrading below 5.131.
                """
            ),
        ] = "5.199",
        storage: Annotated[
            BaseStorage | None,
            Doc(
                """
                FSM storage backend.

                Defaults to :class:`~fastvk.fsm.MemoryStorage` (in-process, lost on restart).
                Pass a persistent backend (e.g. Redis) for production bots.
                """
            ),
        ] = None,
        middleware: Annotated[
            list[BaseMiddleware] | BaseMiddleware | None,
            Doc(
                """
                Middleware applied to every incoming update.

                Can be a single instance or a list.
                Middleware is executed in the order provided.
                """
            ),
        ] = None,
    ) -> None:
        super().__init__()
        self.bot = Bot(token=token, version=api_version)
        self.group_id = group_id
        self.storage: BaseStorage = storage or MemoryStorage()

        if middleware is None:
            _mw: list[BaseMiddleware] = []
        elif isinstance(middleware, list):
            _mw = middleware
        else:
            _mw = [middleware]
        self.middleware_manager = MiddlewareManager(_mw)

    def middleware(self, mw: BaseMiddleware) -> BaseMiddleware:
        """
        Register *mw* as global middleware.

        Can be used as a decorator:

        ```python
        @bot.middleware
        class Log(BaseMiddleware):
            async def __call__(self, handler, event, data):
                print(event)
                return await handler(event, data)
        ```
        """
        self.middleware_manager.register(mw)
        return mw

    async def _process_update(self, update: Update) -> None:
        await self.middleware_manager.trigger(
            lambda evt, data: self.feed_update(update, self.bot, self.storage),
            update,
            {},
        )

    async def _run_polling(self) -> None:
        logger.info("FastVK started (group_id=%d)", self.group_id)
        poller = LongPoller(api=self.bot, group_id=self.group_id)
        try:
            async for update in poller.listen():
                asyncio.create_task(self._process_update(update))
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Polling stopped")
        finally:
            await self.bot.close()
            await self.storage.close()

    def run_polling(self) -> None:
        """
        Start Long Poll and block until interrupted.

        ```python
        if __name__ == "__main__":
            bot.run_polling()
        ```
        """
        try:
            asyncio.run(self._run_polling())
        except KeyboardInterrupt:
            logger.info("FastVK stopped by user")
