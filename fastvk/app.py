from __future__ import annotations

import asyncio
import collections
import logging
import time
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from aiohttp import web


from .api.client import Bot
from .types.group import Group
from .fsm.storage import BaseStorage, MemoryStorage
from .middleware.base import BaseMiddleware, MiddlewareManager
from .middleware.throttling import ThrottlingMiddleware
from .polling.longpoll import LongPoller
from .router import Router
from .types.update import Update
from .logging import setup_logging
from .dashboard.server import Dashboard
from .dashboard.config import BaseDashboard
from .webhook import WebhookHandler


logger = logging.getLogger("fastvk")

Lifespan = Callable[["FastVK"], AbstractAsyncContextManager[None]]


class FastVK(Router):
    def __init__(
        self,
        token: str,
        group_id: int | None = None,
        *,
        storage: BaseStorage | None = None,
        middleware: list[BaseMiddleware] | BaseMiddleware | None = None,
        lifespan: Lifespan | None = None,
        dashboard: BaseDashboard | None = None,
        throttle_rate: float = 1.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        super().__init__()
        self.bot = Bot(token=token, max_retries=max_retries, retry_delay=retry_delay)
        self.group_id: int = group_id or 0
        self.storage: BaseStorage = storage or MemoryStorage()
        self._lifespan: Lifespan | None = lifespan
        self._dashboard = dashboard

        self._stats: dict = {
            "total": 0,
            "handled": 0,
            "errors": 0,
            "by_type": {},
            "started_at": None,
        }
        self._log: collections.deque = collections.deque(maxlen=200)

        if middleware is None:
            _mw: list[BaseMiddleware] = []
        elif isinstance(middleware, list):
            _mw = middleware
        else:
            _mw = [middleware]

        if throttle_rate > 0:
            _mw = [ThrottlingMiddleware(rate=throttle_rate), *_mw]
        self.middleware_manager = MiddlewareManager(_mw)

    async def get_me(self) -> Group:
        """Return info about the community this bot belongs to."""
        return await self.bot.get_me()

    async def collect(
        self,
        method_class: type,
        *,
        max_total: int = 0,
        items_key: str | None = None,
        count: int = 100,
        offset: int = 0,
        **kwargs: object,
    ) -> list[object]:
        """Collect all items from a paginated VK API method.

        Delegates to :meth:`Bot.collect`.

        ```python
        from fastvk.methods import GroupsGetMembers

        members = await bot.collect(GroupsGetMembers, group_id=123)
        ```
        """
        return await self.bot.collect(
            method_class,
            max_total=max_total,
            items_key=items_key,
            count=count,
            offset=offset,
            **kwargs,
        )

    def middleware(self, mw: BaseMiddleware) -> BaseMiddleware:
        self.middleware_manager.register(mw)
        return mw

    async def _process_update(self, update: Update) -> None:
        logger.debug("← %s", update.type)
        self._stats["total"] += 1
        self._stats["by_type"][update.type] = (
            self._stats["by_type"].get(update.type, 0) + 1
        )
        self._log.appendleft({"t": update.type, "s": round(time.time(), 3)})
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

    async def _resolve_group_id(self) -> None:
        if not self.group_id:
            group = await self.bot.get_me()
            self.group_id = group.id
            logger.debug("Resolved group_id=%d from token", self.group_id)

    async def _poll(self) -> None:
        await self._resolve_group_id()
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
        if self._dashboard is not None and self._dashboard.config.dashboard:
            dash = Dashboard(
                self,
                host=self._dashboard.config.dashboard_host,
                port=self._dashboard.config.dashboard_port,
            )
            await dash.start()

        if self._lifespan is not None:
            async with self._lifespan(self):
                await self._poll()
        else:
            await self._poll()

    def run_polling(self) -> None:
        if not logging.root.handlers:
            setup_logging()
        try:
            asyncio.run(self._run_polling())
        except KeyboardInterrupt:
            logger.info("FastVK stopped by user")

    async def _run_webhook(
        self,
        *,
        confirmation_token: str,
        host: str,
        port: int,
        path: str,
        secret: str | None,
    ) -> None:
        await self._resolve_group_id()
        self._stats["started_at"] = time.monotonic()
        logger.info(
            "FastVK webhook mode (group_id=%d)  %s:%d%s",
            self.group_id,
            host,
            port,
            path,
        )

        if self._dashboard is not None and self._dashboard.config.dashboard:
            dash = Dashboard(
                self,
                host=self._dashboard.config.dashboard_host,
                port=self._dashboard.config.dashboard_port,
            )
            await dash.start()

        handler = WebhookHandler(
            self, confirmation_token=confirmation_token, secret=secret
        )
        aioapp = web.Application()
        aioapp.router.add_post(path, handler.handle)

        runner = web.AppRunner(aioapp, access_log=None)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info("Listening at http://%s:%d%s", host, port, path)

        stop_event = asyncio.Event()
        try:
            if self._lifespan is not None:
                async with self._lifespan(self):
                    await stop_event.wait()
            else:
                await stop_event.wait()
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Webhook stopped")
        finally:
            await runner.cleanup()
            await self.bot.close()
            await self.storage.close()

    def run_webhook(
        self,
        *,
        confirmation_token: str,
        host: str = "0.0.0.0",
        port: int = 8080,
        path: str = "/",
        secret: str | None = None,
    ) -> None:
        """
        Start an aiohttp server that receives VK Callback API events.

        *confirmation_token* — the string shown in VK group settings
        under API → Callback API → Confirmation code.

        ```python
        bot.run_webhook(
            confirmation_token="abc123",
            host="0.0.0.0",
            port=8080,
            path="/vk",
            secret="my_secret",   # optional
        )
        ```
        """
        if not logging.root.handlers:
            setup_logging()
        try:
            asyncio.run(
                self._run_webhook(
                    confirmation_token=confirmation_token,
                    host=host,
                    port=port,
                    path=path,
                    secret=secret,
                )
            )
        except KeyboardInterrupt:
            logger.info("FastVK stopped by user")
