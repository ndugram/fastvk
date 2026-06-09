from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

if TYPE_CHECKING:
    from ..api.client import Bot
    from ..enums.chat_action import ChatAction
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
        dont_parse_links: bool = False,
        disable_mentions: bool = False,
    ) -> int:
        assert self._bot is not None
        return await self._bot.messages.send(
            peer_id=self.peer_id,
            message=text,
            random_id=random.randint(0, 2**31),
            keyboard=str(keyboard) if keyboard is not None else None,
            content_source=str(parse_mode) if parse_mode is not None else None,
            dont_parse_links=int(dont_parse_links) if dont_parse_links else None,
            disable_mentions=int(disable_mentions) if disable_mentions else None,
        )

    async def reply(
        self,
        text: str,
        *,
        keyboard: Keyboard | str | None = None,
        dont_parse_links: bool = False,
        disable_mentions: bool = False,
    ) -> int:
        assert self._bot is not None
        return await self._bot.messages.send(
            peer_id=self.peer_id,
            message=text,
            reply_to=self.id,
            random_id=random.randint(0, 2**31),
            keyboard=str(keyboard) if keyboard is not None else None,
            dont_parse_links=int(dont_parse_links) if dont_parse_links else None,
            disable_mentions=int(disable_mentions) if disable_mentions else None,
        )

    async def answer_photo(
        self,
        attachment: str,
        caption: str = "",
        *,
        keyboard: Keyboard | str | None = None,
        dont_parse_links: bool = False,
        disable_mentions: bool = False,
    ) -> int:
        """Send a photo. ``attachment`` — VK attachment string, e.g. ``"photo-1_2"``."""
        assert self._bot is not None
        return await self._bot.messages.send(
            peer_id=self.peer_id,
            message=caption,
            attachment=attachment,
            random_id=random.randint(0, 2**31),
            keyboard=str(keyboard) if keyboard is not None else None,
            dont_parse_links=int(dont_parse_links) if dont_parse_links else None,
            disable_mentions=int(disable_mentions) if disable_mentions else None,
        )

    async def answer_doc(
        self,
        attachment: str,
        caption: str = "",
        *,
        keyboard: Keyboard | str | None = None,
        dont_parse_links: bool = False,
        disable_mentions: bool = False,
    ) -> int:
        """Send a document. ``attachment`` — VK attachment string, e.g. ``"doc-1_2"``."""
        assert self._bot is not None
        return await self._bot.messages.send(
            peer_id=self.peer_id,
            message=caption,
            attachment=attachment,
            random_id=random.randint(0, 2**31),
            keyboard=str(keyboard) if keyboard is not None else None,
            dont_parse_links=int(dont_parse_links) if dont_parse_links else None,
            disable_mentions=int(disable_mentions) if disable_mentions else None,
        )

    async def answer_video(
        self,
        attachment: str,
        caption: str = "",
        *,
        keyboard: Keyboard | str | None = None,
        dont_parse_links: bool = False,
        disable_mentions: bool = False,
    ) -> int:
        """Send a video. ``attachment`` — VK attachment string, e.g. ``"video-1_2"``."""
        assert self._bot is not None
        return await self._bot.messages.send(
            peer_id=self.peer_id,
            message=caption,
            attachment=attachment,
            random_id=random.randint(0, 2**31),
            keyboard=str(keyboard) if keyboard is not None else None,
            dont_parse_links=int(dont_parse_links) if dont_parse_links else None,
            disable_mentions=int(disable_mentions) if disable_mentions else None,
        )

    async def answer_sticker(self, sticker_id: int) -> int:
        """Send a sticker."""
        assert self._bot is not None
        return await self._bot.messages.send(
            peer_id=self.peer_id,
            sticker_id=sticker_id,
            random_id=random.randint(0, 2**31),
        )

    async def forward(self, peer_id: int | None = None) -> int:
        """Forward this message to *peer_id* (defaults to same conversation)."""
        assert self._bot is not None
        return await self._bot.messages.send(
            peer_id=peer_id if peer_id is not None else self.peer_id,
            forward_messages=self.id,
            random_id=random.randint(0, 2**31),
        )

    async def edit(
        self,
        text: str,
        *,
        keyboard: Keyboard | str | None = None,
        attachment: str | None = None,
        dont_parse_links: bool = False,
        disable_mentions: bool = False,
    ) -> int:
        """Edit this message."""
        assert self._bot is not None
        return await self._bot.messages.edit(
            peer_id=self.peer_id,
            message_id=self.id,
            message=text,
            keyboard=str(keyboard) if keyboard is not None else None,
            attachment=attachment,
            dont_parse_links=int(dont_parse_links) if dont_parse_links else None,
            disable_mentions=int(disable_mentions) if disable_mentions else None,
        )

    async def typing(self, action: ChatAction | str = "typing") -> None:
        """Send a chat action indicator (default: "печатает...")."""
        assert self._bot is not None
        await self._bot.messages.setActivity(
            peer_id=self.peer_id,
            type=str(action),
        )

    async def delete(self, *, delete_for_all: bool = False) -> int:
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
