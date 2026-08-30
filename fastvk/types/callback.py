from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

if TYPE_CHECKING:
    from ..api.client import Bot
    from .user import User


class CallbackQuery(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: int
    peer_id: int
    event_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    conversation_message_id: int = 0

    _bot: Bot | None = PrivateAttr(default=None)
    _from_user: User | None = PrivateAttr(default=None)

    @property
    def from_user(self) -> User | None:
        return self._from_user

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

    async def answer(
        self,
        text: str = "",
        *,
        link: str | None = None,
        app_hash: str | None = None,
    ) -> None:
        """Respond to the click: show a snackbar, open a link, or open the community app."""
        assert self._bot is not None
        if link is not None:
            event_data = json.dumps({"type": "open_link", "link": link}, ensure_ascii=False)
        elif app_hash is not None:
            event_data = json.dumps(
                {"type": "open_app", "app_id": None, "hash": app_hash}, ensure_ascii=False
            )
        else:
            event_data = json.dumps({"type": "show_snackbar", "text": text}, ensure_ascii=False)
        await self._bot.messages.sendMessageEventAnswer(
            event_id=self.event_id,
            user_id=self.user_id,
            peer_id=self.peer_id,
            event_data=event_data,
        )

    async def edit_message(
        self,
        text: str,
        *,
        keyboard: Any = None,
        attachment: str | None = None,
    ) -> int:
        """Edit the message the pressed button belongs to."""
        assert self._bot is not None
        return await self._bot.messages.edit(
            peer_id=self.peer_id,
            conversation_message_id=self.conversation_message_id,
            message=text,
            keyboard=str(keyboard) if keyboard is not None else None,
            attachment=attachment,
        )
