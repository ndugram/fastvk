from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any

from .api.client import Bot
from .fsm.storage import BaseStorage, MemoryStorage
from .router import Router
from .types.update import Update


class MockedBot(Bot):
    """
    A :class:`~fastvk.Bot` that never touches the network.

    Records every API call and returns canned responses, so handlers can be
    exercised in unit tests without a token.

    ```python
    bot = MockedBot()
    bot.set_result("messages.send", 42)
    bot.set_result("users.get", [{"id": 1, "first_name": "A", "last_name": "B"}])

    await dispatch(my_router, bot, message_update(text="/start"))
    assert bot.calls[-1].method == "messages.send"
    ```
    """

    class Call:
        __slots__ = ("method", "params")

        def __init__(self, method: str, params: dict[str, Any]) -> None:
            self.method = method
            self.params = params

        def __repr__(self) -> str:
            return f"Call({self.method!r}, {self.params!r})"

    def __init__(self, token: str = "test-token") -> None:
        super().__init__(token=token)
        self.calls: list[MockedBot.Call] = []
        self._results: dict[str, Any] = {
            "users.get": [{"id": 1, "first_name": "Test", "last_name": "User"}],
            "messages.send": 1,
            "messages.edit": 1,
            "messages.sendMessageEventAnswer": 1,
        }

    def set_result(self, method: str, value: Any) -> None:
        """Set what a given VK method call should return."""
        self._results[method] = value

    async def _call(self, method: str, **kwargs: Any) -> Any:
        self.calls.append(MockedBot.Call(method, kwargs))
        result = self._results.get(method)
        return result() if callable(result) else result

    async def close(self) -> None:
        return None

    # -- assertions --------------------------------------------------------

    def assert_called(self, method: str) -> MockedBot.Call:
        for call in reversed(self.calls):
            if call.method == method:
                return call
        raise AssertionError(
            f"{method!r} was not called. Calls: {[c.method for c in self.calls]}"
        )

    def assert_not_called(self, method: str) -> None:
        if any(c.method == method for c in self.calls):
            raise AssertionError(f"{method!r} was called unexpectedly")

    @property
    def sent_messages(self) -> list[dict[str, Any]]:
        return [c.params for c in self.calls if c.method == "messages.send"]


def message_update(
    text: str = "",
    *,
    from_id: int = 1,
    peer_id: int = 1,
    msg_id: int = 1,
    attachments: Sequence[dict[str, Any]] | None = None,
    payload: str | None = None,
    group_id: int = 1,
    event_id: str | None = None,
) -> Update:
    """Build a ``message_new`` :class:`~fastvk.types.Update` for tests."""
    return Update(
        type="message_new",
        object={
            "message": {
                "id": msg_id,
                "date": int(time.time()),
                "peer_id": peer_id,
                "from_id": from_id,
                "text": text,
                "attachments": list(attachments or []),
                "payload": payload,
            }
        },
        group_id=group_id,
        event_id=event_id or f"evt-{msg_id}",
    )


def callback_update(
    payload: str = "{}",
    *,
    user_id: int = 1,
    peer_id: int = 1,
    cmid: int = 1,
    group_id: int = 1,
    event_id: str = "evt-cb",
) -> Update:
    """Build a ``message_event`` :class:`~fastvk.types.Update` for tests."""
    return Update(
        type="message_event",
        object={
            "user_id": user_id,
            "peer_id": peer_id,
            "event_id": event_id,
            "payload": payload,
            "conversation_message_id": cmid,
        },
        group_id=group_id,
        event_id=event_id,
    )


async def dispatch(
    router: Router,
    bot: Bot,
    update: Update,
    *,
    storage: BaseStorage | None = None,
    data: dict[Any, Any] | None = None,
) -> bool:
    """Feed *update* through *router* and return whether it was handled."""
    return await router.feed_update(update, bot, storage or MemoryStorage(), data)


__all__ = ["MockedBot", "message_update", "callback_update", "dispatch"]
