from __future__ import annotations

import json
import logging
import time
from typing import TYPE_CHECKING

from aiohttp import web

from .html import get_dashboard_html
from ..__meta__ import __version__, _api_version_

if TYPE_CHECKING:
    from ..app import FastVK

logger = logging.getLogger("fastvk.dashboard")


class Dashboard:
    def __init__(self, app: FastVK, *, host: str = "127.0.0.1", port: int = 8080) -> None:
        self._app = app
        self._host = host
        self._port = port
        self._runner: web.AppRunner | None = None

    async def _handle_index(self, request: web.Request) -> web.Response:
        html = get_dashboard_html(version=__version__, group_id=self._app.group_id)
        return web.Response(text=html, content_type="text/html")

    async def _handle_info(self, request: web.Request) -> web.Response:
        handlers = []
        for h in self._app._collect_all_handlers():
            handlers.append({
                "event": h.event_type,
                "handler": h.callback.__name__,
                "module": getattr(h.callback, "__module__", ""),
                "filters": [type(f).__name__ for f in h.filters],
            })
        return web.Response(
            text=json.dumps({
                "group_id": self._app.group_id,
                "version": __version__,
                "api_version": _api_version_,
                "handlers": handlers,
            }),
            content_type="application/json",
        )

    async def _handle_stats(self, request: web.Request) -> web.Response:
        stats = self._app._stats
        uptime = time.monotonic() - stats["started_at"] if stats.get("started_at") else 0
        return web.Response(
            text=json.dumps({
                "total": stats["total"],
                "handled": stats["handled"],
                "errors": stats["errors"],
                "by_type": stats["by_type"],
                "uptime_seconds": round(uptime, 1),
            }),
            content_type="application/json",
        )

    async def start(self) -> None:
        aioapp = web.Application()
        aioapp.router.add_get("/", self._handle_index)
        aioapp.router.add_get("/api/info", self._handle_info)
        aioapp.router.add_get("/api/stats", self._handle_stats)
        aioapp.router.add_get("/api/log", self._handle_log)

        self._runner = web.AppRunner(aioapp, access_log=None)
        await self._runner.setup()

        port = self._port
        for _ in range(10):
            try:
                site = web.TCPSite(self._runner, self._host, port)
                await site.start()
                break
            except OSError:
                port += 1
        else:
            logger.warning("Dashboard could not bind to any port in %d-%d", self._port, port)
            return

        self._port = port
        logger.info("Dashboard running at http://%s:%d", self._host, self._port)

    async def _handle_log(self, request: web.Request) -> web.Response:
        return web.Response(
            text=json.dumps(list(self._app._log)),
            content_type="application/json",
        )

    async def stop(self) -> None:
        if self._runner:
            await self._runner.cleanup()
