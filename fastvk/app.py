from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from .api.client import Bot
from .fsm.storage import BaseStorage, MemoryStorage
from .middleware.base import BaseMiddleware, MiddlewareManager
from .polling.longpoll import LongPoller
from .router import Router
from .types.update import Update

logger = logging.getLogger("fastvk")

Lifespan = Callable[["FastVK"], AbstractAsyncContextManager[None]]


class FastVK(Router):
    def __init__(
        self,
        token: str,
        group_id: int,
        *,
        storage: BaseStorage | None = None,
        middleware: list[BaseMiddleware] | BaseMiddleware | None = None,
        lifespan: Lifespan | None = None,
    ) -> None:
        super().__init__()
        self.bot = Bot(token=token)
        self.group_id = group_id
        self.storage: BaseStorage = storage or MemoryStorage()
        self._lifespan: Lifespan | None = lifespan

        if middleware is None:
            _mw: list[BaseMiddleware] = []
        elif isinstance(middleware, list):
            _mw = middleware
        else:
            _mw = [middleware]
        self.middleware_manager = MiddlewareManager(_mw)

    def middleware(self, mw: BaseMiddleware) -> BaseMiddleware:
        self.middleware_manager.register(mw)
        return mw

    async def _process_update(self, update: Update) -> None:
        logger.info("Update: %s", update.type)
        handled = await self.middleware_manager.trigger(
            lambda evt, data: self.feed_update(update, self.bot, self.storage),
            update,
            {},
        )
        if not handled:
            logger.debug("No handler for %s", update.type)

    async def _poll(self) -> None:
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

    async def _run_polling(self) -> None:
        if self._lifespan is not None:
            async with self._lifespan(self):
                await self._poll()
        else:
            await self._poll()

    def run_polling(self) -> None:
        if not logging.root.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
                datefmt="%H:%M:%S",
            )
        try:
            asyncio.run(self._run_polling())
        except KeyboardInterrupt:
            logger.info("FastVK stopped by user")
