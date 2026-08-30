from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

import aiohttp

from ..types.update import Update

if TYPE_CHECKING:
    from ..api.client import Bot

logger = logging.getLogger("fastvk.polling")

_EVENT_NEW_MESSAGE = 4
_EVENT_EDIT_MESSAGE = 5

# message flag bit — set on messages sent by the account itself
_FLAG_OUTBOX = 2


class UserLongPoller:
    """
    Long Poll for **user** tokens (``messages.getLongPollServer``).

    Yields :class:`~fastvk.types.Update` objects shaped like group updates so
    the same routers/handlers work:

    - new incoming message  → ``type="message_new"``
    - edited message        → ``type="message_edit"``
    - anything else         → ``type="raw"`` with ``object={"event": [...]}``

    ```python
    poller = UserLongPoller(api=bot, wait=25)
    async for update in poller.listen():
        ...
    ```
    """

    def __init__(self, api: Bot, wait: int = 25) -> None:
        self.api = api
        self.wait = wait
        self._mode = 2 + 8 + 64 + 128  # attachments + extended + random_id + more

    async def _get_server(self) -> tuple[str, str, str]:
        data = await self.api._call("messages.getLongPollServer", lp_version=3, need_pts=0)
        return data["server"], data["key"], str(data["ts"])

    def _to_update(self, event: list[Any]) -> Update:
        code = event[0]
        if code in (_EVENT_NEW_MESSAGE, _EVENT_EDIT_MESSAGE):
            _, msg_id, flags, peer_id, ts, text, *rest = event
            extra: dict[str, Any] = rest[0] if rest and isinstance(rest[0], dict) else {}
            attach: dict[str, Any] = rest[1] if len(rest) > 1 and isinstance(rest[1], dict) else {}
            from_id = int(attach.get("from") or extra.get("from") or peer_id)
            message = {
                "id": msg_id,
                "date": ts,
                "peer_id": peer_id,
                "from_id": from_id,
                "text": text,
                "out": 1 if flags & _FLAG_OUTBOX else 0,
                "attachments": [],
                "_lp_attach": attach,
            }
            u_type = "message_new" if code == _EVENT_NEW_MESSAGE else "message_edit"
            return Update(
                type=u_type,
                object={"message": message},
                group_id=0,
                event_id=f"lp-{msg_id}-{ts}",
            )
        return Update(
            type="raw",
            object={"event": event},
            group_id=0,
            event_id=f"lp-raw-{event[1] if len(event) > 1 else ''}",
        )

    async def listen(self) -> AsyncIterator[Update]:
        server, key, ts = await self._get_server()
        session = await self.api._get_session()
        lp_timeout = aiohttp.ClientTimeout(total=self.wait + 15)
        logger.info("User Long Poll started")

        while True:
            try:
                url = (
                    f"https://{server}?act=a_check&key={key}&ts={ts}"
                    f"&wait={self.wait}&mode={self._mode}&version=3"
                )
                async with session.get(url, timeout=lp_timeout) as resp:
                    data: dict = await resp.json(content_type=None)

                failed = data.get("failed")
                if failed is not None:
                    if failed == 1:
                        ts = str(data["ts"])
                    else:
                        logger.warning("User Long Poll failed=%d, re-fetching", failed)
                        server, key, ts = await self._get_server()
                    continue

                ts = str(data["ts"])
                for event in data.get("updates", []):
                    if isinstance(event, list) and event:
                        yield self._to_update(event)

            except (asyncio.CancelledError, KeyboardInterrupt):
                return
            except Exception as exc:
                logger.error("User Long Poll error: %s", exc)
                await asyncio.sleep(1)
                try:
                    server, key, ts = await self._get_server()
                except Exception:
                    await asyncio.sleep(5)


__all__ = ["UserLongPoller"]
