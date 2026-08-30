from __future__ import annotations

import asyncio
import collections
import contextlib
import logging
import signal
import time
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from aiohttp import web


from typing import TYPE_CHECKING, Any

from .api.client import Bot
from .types.group import Group

if TYPE_CHECKING:
    from .api.client import _APIMethod
from .fsm.storage import BaseStorage, MemoryStorage
from .middleware.base import BaseMiddleware, MiddlewareManager
from .middleware.throttling import ThrottlingMiddleware
from .polling.longpoll import LongPoller
from .polling.userlongpoll import UserLongPoller
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
        timeout: float = 30.0,
        max_concurrency: int = 0,
        polling: str = "group",
    ) -> None:
        super().__init__()
        if polling not in ("group", "user"):
            raise ValueError("polling must be 'group' or 'user'")
        self._polling_mode = polling
        self.bot = Bot(
            token=token,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )
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

        self._tasks: set[asyncio.Task] = set()
        self._sem: asyncio.Semaphore | None = (
            asyncio.Semaphore(max_concurrency) if max_concurrency > 0 else None
        )
        self._stopping = asyncio.Event()
        self._seen_events: collections.OrderedDict[str, None] = collections.OrderedDict()

        if middleware is None:
            _mw: list[BaseMiddleware] = []
        elif isinstance(middleware, list):
            _mw = middleware
        else:
            _mw = [middleware]

        if throttle_rate > 0:
            _mw = [ThrottlingMiddleware(rate=throttle_rate), *_mw]
        self.middleware_manager = MiddlewareManager(_mw)

    @property
    def uploader(self) -> Any:  # noqa: ANN401
        """Lazy :class:`~fastvk.upload.Uploader` bound to this bot."""
        from .upload import Uploader

        cached = getattr(self, "_uploader", None)
        if cached is None:
            cached = Uploader(self.bot)
            self._uploader = cached
        return cached

    @property
    def messages(self) -> _APIMethod:
        """VK API methods namespace: send, edit, delete, etc."""
        return self.bot.messages

    @property
    def users(self) -> _APIMethod:
        """VK API methods namespace: get, search."""
        return self.bot.users

    @property
    def groups(self) -> _APIMethod:
        """VK API methods namespace: getById, getMembers, etc."""
        return self.bot.groups

    @property
    def wall(self) -> _APIMethod:
        """VK API methods namespace: get, post, getById."""
        return self.bot.wall

    @property
    def photos(self) -> _APIMethod:
        """VK API methods namespace: getMessagesUploadServer, saveMessagesPhoto."""
        return self.bot.photos

    @property
    def docs(self) -> _APIMethod:
        """VK API methods namespace: getMessagesUploadServer, save."""
        return self.bot.docs

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

    def _is_duplicate(self, event_id: str) -> bool:
        if not event_id:
            return False
        if event_id in self._seen_events:
            return True
        self._seen_events[event_id] = None
        if len(self._seen_events) > 10_000:
            self._seen_events.popitem(last=False)
        return False

    async def _process_update(self, update: Update) -> None:
        if self._is_duplicate(update.event_id):
            logger.debug("↺ %s  [duplicate event_id=%s]", update.type, update.event_id)
            return
        logger.debug("← %s", update.type)
        self._stats["total"] += 1
        self._stats["by_type"][update.type] = (
            self._stats["by_type"].get(update.type, 0) + 1
        )
        self._log.appendleft({"t": update.type, "s": round(time.time(), 3)})

        data: dict = {}

        async def _run_handlers(evt: object, d: dict) -> bool:
            return await self.feed_update(update, self.bot, self.storage, d)

        try:
            handled = await self.middleware_manager.trigger(_run_handlers, update, data)
            if handled:
                self._stats["handled"] += 1
            else:
                logger.debug("← %s  [no handler]", update.type)
        except Exception:
            self._stats["errors"] += 1
            logger.exception("Update processing failed: %s", update.type)

    def _spawn(self, update: Update) -> None:
        async def _guarded() -> None:
            if self._sem is not None:
                async with self._sem:
                    await self._process_update(update)
            else:
                await self._process_update(update)

        task = asyncio.create_task(_guarded())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _drain(self, timeout: float = 10.0) -> None:
        if not self._tasks:
            return
        logger.info("Waiting for %d in-flight update(s)…", len(self._tasks))
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(
                asyncio.gather(*self._tasks, return_exceptions=True), timeout
            )
        for t in self._tasks:
            t.cancel()

    async def _resolve_group_id(self) -> None:
        if not self.group_id:
            group = await self.bot.get_me()
            self.group_id = group.id
            logger.debug("Resolved group_id=%d from token", self.group_id)

    def _install_signal_handlers(self, loop: asyncio.AbstractEventLoop) -> None:
        for sig in (signal.SIGINT, signal.SIGTERM):
            with contextlib.suppress(NotImplementedError):
                loop.add_signal_handler(sig, self._stopping.set)

    async def _poll(self) -> None:
        self._stats["started_at"] = time.monotonic()
        if self._polling_mode == "user":
            logger.info("FastVK started (user long poll)")
            poller: Any = UserLongPoller(api=self.bot, wait=25)
        else:
            await self._resolve_group_id()
            logger.info("FastVK started (group_id=%d)", self.group_id)
            poller = LongPoller(api=self.bot, group_id=self.group_id)
        listener = poller.listen()
        try:
            while not self._stopping.is_set():
                nxt = asyncio.ensure_future(listener.__anext__())
                stop = asyncio.ensure_future(self._stopping.wait())
                done, _ = await asyncio.wait(
                    {nxt, stop}, return_when=asyncio.FIRST_COMPLETED
                )
                if stop in done:
                    nxt.cancel()
                    with contextlib.suppress(Exception):
                        await nxt
                    break
                stop.cancel()
                try:
                    update = nxt.result()
                except StopAsyncIteration:
                    break
                self._spawn(update)
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Polling stopped")
        finally:
            with contextlib.suppress(Exception):
                await listener.aclose()
            await self._drain()
            await self.bot.close()
            await self.storage.close()

    async def _run_polling(self) -> None:
        loop = asyncio.get_running_loop()
        self._install_signal_handlers(loop)

        if self._dashboard is not None and self._dashboard.config.dashboard:
            dash = Dashboard(
                self,
                host=self._dashboard.config.dashboard_host,
                port=self._dashboard.config.dashboard_port,
            )
            await dash.start()

        context = {FastVK: self, Bot: self.bot}
        await self._emit_startup(context)
        try:
            if self._lifespan is not None:
                async with self._lifespan(self):
                    await self._poll()
            else:
                await self._poll()
        finally:
            await self._emit_shutdown(context)

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
        loop = asyncio.get_running_loop()
        self._install_signal_handlers(loop)

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
        from .metrics import render_prometheus

        async def _health(_r: web.Request) -> web.Response:
            return web.json_response({"status": "ok"})

        async def _metrics(_r: web.Request) -> web.Response:
            return web.Response(
                text=render_prometheus(self), content_type="text/plain"
            )

        aioapp = web.Application()
        aioapp.router.add_post(path, handler.handle)
        aioapp.router.add_get("/health", _health)
        aioapp.router.add_get("/metrics", _metrics)

        runner = web.AppRunner(aioapp, access_log=None)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info("Listening at http://%s:%d%s", host, port, path)

        context = {FastVK: self, Bot: self.bot}
        await self._emit_startup(context)
        try:
            if self._lifespan is not None:
                async with self._lifespan(self):
                    await self._stopping.wait()
            else:
                await self._stopping.wait()
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Webhook stopped")
        finally:
            await self._emit_shutdown(context)
            await self._drain()
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
