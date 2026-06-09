from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

if TYPE_CHECKING:
    from ..api.client import Bot


class CallbackQuery(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: int
    peer_id: int
    event_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    conversation_message_id: int = 0

    _bot: Bot | None = PrivateAttr(default=None)

    @classmethod
    def from_dict(cls, data: dict[str, Any], bot: Bot) -> CallbackQuery:
        raw_payload = data.get("payload", "{}")
        try:
            payload = json.loads(raw_payload) if isinstance(raw_payload, str) else raw_payload
        except (json.JSONDecodeError, TypeError):
            payload = {}
        obj = cls(
            user_id=data["user_id"],
            peer_id=data["peer_id"],
            event_id=data["event_id"],
            payload=payload or {},
            conversation_message_id=data.get("conversation_message_id", 0),
        )
        obj._bot = bot
        return obj

    async def answer(self, text: str = "", *, link: str | None = None) -> None:
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
