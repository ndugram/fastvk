from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from ..types.update import Update

if TYPE_CHECKING:
    from ..api.client import Bot

logger = logging.getLogger("fastvk.polling")


class LongPoller:
    """
    Async generator that continuously yields :class:`~fastvk.types.Update`
    objects from the VK Group Long Poll API.

    Handles reconnection on failures automatically:

    - ``failed: 1`` → update ``ts`` and continue.
    - ``failed: 2 / 3`` → re-fetch server info.
    - Network errors → sleep 1 s, then retry.

    ```python
    poller = LongPoller(api=api, group_id=123)
    async for update in poller.listen():
        print(update.type, update.object)
    ```
    """

    def __init__(
        self,
        api: Bot,
        group_id: int,
        wait: int = 25,
    ) -> None:
        self.api = api
        self.group_id = group_id
        self.wait = wait

    async def _get_server(self) -> tuple[str, str, str]:
        data = await self.api.groups.getLongPollServer(group_id=self.group_id)
        return data["server"], data["key"], data["ts"]

    async def listen(self) -> AsyncIterator[Update]:
        """Yield updates indefinitely until cancelled."""
        server, key, ts = await self._get_server()
        session = await self.api._get_session()
        logger.info("Polling started")

        while True:
            try:
                url = (
                    f"{server}"
                    f"?act=a_check&key={key}&ts={ts}&wait={self.wait}"
                )
                async with session.get(url) as resp:
                    data: dict = await resp.json(content_type=None)

                failed = data.get("failed")
                if failed is not None:
                    if failed == 1:
                        ts = data["ts"]
                    else:
                        logger.warning("Long poll failed=%d, re-fetching server", failed)
                        server, key, ts = await self._get_server()
                    continue

                ts = data["ts"]
                for raw in data.get("updates", []):
                    update = Update(
                        type=raw["type"],
                        object=raw["object"],
                        group_id=raw.get("group_id", self.group_id),
                        event_id=raw.get("event_id", ""),
                    )
                    logger.debug("Update: %s", update.type)
                    yield update

            except (asyncio.CancelledError, KeyboardInterrupt):
                return

            except Exception as exc:
                logger.error("Long poll error: %s", exc)
                await asyncio.sleep(1)
                try:
                    server, key, ts = await self._get_server()
                except Exception:
                    await asyncio.sleep(5)
