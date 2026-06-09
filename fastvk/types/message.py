from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

if TYPE_CHECKING:
    from ..api.client import Bot
    from ..enums.parse_mode import ParseMode
    from ..keyboard import Keyboard
    from .user import User


class Message(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: int
    date: int
    peer_id: int
    from_id: int
    text: str = ""
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    reply_message: dict[str, Any] | None = None
    fwd_messages: list[dict[str, Any]] = Field(default_factory=list)
    payload: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

    _bot: Bot | None = PrivateAttr(default=None)
    _from_user: User | None = PrivateAttr(default=None)

    @property
    def from_user(self) -> User | None:
        return self._from_user

    @classmethod
    def from_dict(cls, data: dict[str, Any], bot: Bot) -> Message:
        obj = cls(
            id=data["id"],
            date=data["date"],
            peer_id=data["peer_id"],
            from_id=data["from_id"],
            text=data.get("text", ""),
            attachments=data.get("attachments", []),
            reply_message=data.get("reply_message"),
            fwd_messages=data.get("fwd_messages", []),
            payload=data.get("payload"),
            raw=data,
        )
        obj._bot = bot
        return obj

    async def answer(
        self,
        text: str,
        *,
        keyboard: Keyboard | str | None = None,
        parse_mode: ParseMode | str | None = None,
        **kwargs: Any,
    ) -> Any:
        assert self._bot is not None
        if keyboard is not None:
            kwargs["keyboard"] = str(keyboard)
        if parse_mode is not None:
            kwargs["content_source"] = str(parse_mode)
        return await self._bot.messages.send(
            peer_id=self.peer_id,
            message=text,
            random_id=random.randint(0, 2**31),
            **kwargs,
        )

    async def reply(
        self,
        text: str,
        *,
        keyboard: Keyboard | str | None = None,
        **kwargs: Any,
    ) -> Any:
        assert self._bot is not None
        if keyboard is not None:
            kwargs["keyboard"] = str(keyboard)
        return await self._bot.messages.send(
            peer_id=self.peer_id,
            message=text,
            reply_to=self.id,
            random_id=random.randint(0, 2**31),
            **kwargs,
        )

    async def delete(self, *, delete_for_all: bool = False) -> Any:
        assert self._bot is not None
        return await self._bot.messages.delete(
            message_ids=self.id,
            delete_for_all=int(delete_for_all),
        )

    @property
    def is_private(self) -> bool:
        return 0 < self.peer_id < 2_000_000_000

    @property
    def is_chat(self) -> bool:
        return self.peer_id > 2_000_000_000

    @property
    def chat_id(self) -> int | None:
        return self.peer_id - 2_000_000_000 if self.is_chat else None
