from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from aiohttp import web

from .types.update import Update

if TYPE_CHECKING:
    from .app import FastVK

logger = logging.getLogger("fastvk.webhook")


class WebhookHandler:
    """
    aiohttp request handler for VK Callback API.

    Handles the one-time confirmation handshake and dispatches
    subsequent events to the FastVK app.
    """

    def __init__(
        self,
        app: FastVK,
        *,
        confirmation_token: str,
        secret: str | None = None,
    ) -> None:
        self._app = app
        self._confirmation_token = confirmation_token
        self._secret = secret

    async def handle(self, request: web.Request) -> web.Response:
        try:
            data: dict = await request.json()
        except Exception:
            return web.Response(text="bad request", status=400)

        if self._secret and data.get("secret") != self._secret:
            logger.warning("Webhook secret mismatch — request rejected")
            return web.Response(text="forbidden", status=403)

        if data.get("type") == "confirmation":
            return web.Response(text=self._confirmation_token)

        try:
            update = Update(
                type=data["type"],
                object=data["object"],
                group_id=data.get("group_id", self._app.group_id),
                event_id=data.get("event_id", ""),
            )
            asyncio.create_task(self._app._process_update(update))
        except Exception as exc:
            logger.error("Webhook parse error: %s", exc)

        return web.Response(text="ok")
