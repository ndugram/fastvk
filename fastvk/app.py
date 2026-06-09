from __future__ import annotations

import asyncio
import logging
import time
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
        dashboard: bool = False,
        dashboard_host: str = "127.0.0.1",
        dashboard_port: int = 8080,
    ) -> None:
        super().__init__()
        self.bot = Bot(token=token)
        self.group_id = group_id
        self.storage: BaseStorage = storage or MemoryStorage()
        self._lifespan: Lifespan | None = lifespan
        self._dashboard_enabled = dashboard
        self._dashboard_host = dashboard_host
        self._dashboard_port = dashboard_port

        self._stats: dict = {
            "total": 0,
            "handled": 0,
            "errors": 0,
            "by_type": {},
            "started_at": None,
        }

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
        logger.debug("← %s", update.type)
        self._stats["total"] += 1
        self._stats["by_type"][update.type] = self._stats["by_type"].get(update.type, 0) + 1
        try:
            handled = await self.middleware_manager.trigger(
                lambda evt, data: self.feed_update(update, self.bot, self.storage),
                update,
                {},
            )
            if handled:
                self._stats["handled"] += 1
            else:
                logger.debug("← %s  [no handler]", update.type)
        except Exception:
            self._stats["errors"] += 1
            raise

    async def _poll(self) -> None:
        self._stats["started_at"] = time.monotonic()
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
        if self._dashboard_enabled:
            from .dashboard.server import Dashboard
            dash = Dashboard(self, host=self._dashboard_host, port=self._dashboard_port)
            await dash.start()

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
