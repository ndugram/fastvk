from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..api.client import Bot


@dataclass(slots=True)
class CallbackQuery:
    """
    Inline button press (``message_event``).

    ```python
    @router.callback()
    async def on_click(callback: CallbackQuery) -> None:
        v = callback.payload.get("v")
        await callback.answer(f"Нажато: {v}")
    ```
    """

    user_id: int
    peer_id: int
    event_id: str
    payload: dict[str, Any]
    conversation_message_id: int
    _bot: Bot | None = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any], bot: Bot) -> CallbackQuery:
        raw_payload = data.get("payload", "{}")
        try:
            payload = json.loads(raw_payload) if isinstance(raw_payload, str) else raw_payload
        except (json.JSONDecodeError, TypeError):
            payload = {}
        return cls(
            user_id=data["user_id"],
            peer_id=data["peer_id"],
            event_id=data["event_id"],
            payload=payload,
            conversation_message_id=data.get("conversation_message_id", 0),
            _bot=bot,
        )

    async def answer(self, text: str = "", *, link: str | None = None) -> None:
        """
        Answer the button press.

        ``text`` — snackbar notification shown to the user.
        ``link`` — open a URL instead of showing a snackbar.

        ```python
        await callback.answer("Готово!")
        await callback.answer(link="https://github.com")
        ```
        """
        assert self._bot is not None
        if link is not None:
            event_data = json.dumps({"type": "open_link", "link": link}, ensure_ascii=False)
        else:
            event_data = json.dumps({"type": "show_snackbar", "text": text}, ensure_ascii=False)
        await self._bot.messages.sendMessageEventAnswer(
            event_id=self.event_id,
            user_id=self.user_id,
            peer_id=self.peer_id,
            event_data=event_data,
        )
