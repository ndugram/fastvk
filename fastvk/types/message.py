from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..api.client import APIClient


@dataclass(slots=True)
class Message:
    """
    Incoming VK message.

    Constructed from a ``message_new`` event payload and enriched
    with helper methods that wrap the VK ``messages.*`` API.

    ```python
    @router.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer("Привет!")
    ```
    """

    id: int
    """Message ID."""

    date: int
    """Unix timestamp of when the message was sent."""

    peer_id: int
    """
    Conversation ID.

    - ``> 0`` and ``< 2_000_000_000`` — private conversation with user.
    - ``< 0`` — community wall.
    - ``> 2_000_000_000`` — multi-user chat (``peer_id - 2_000_000_000`` = chat id).
    """

    from_id: int
    """ID of the user or community that sent the message."""

    text: str
    """Plain text body of the message."""

    attachments: list[dict] = field(default_factory=list)
    """List of raw attachment objects (photos, docs, stickers, etc.)."""

    reply_message: dict | None = None
    """The message this one replies to, or ``None``."""

    fwd_messages: list[dict] = field(default_factory=list)
    """Forwarded messages included in this message."""

    payload: str | None = None
    """Keyboard button payload, if the message was sent via a bot keyboard."""

    raw: dict = field(default_factory=dict)
    """Full raw message object as received from VK."""

    _api: APIClient | None = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: dict, api: APIClient) -> Message:
        """Build a :class:`Message` from a raw VK message dict."""
        return cls(
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
            _api=api,
        )

    async def answer(self, text: str, **kwargs: Any) -> Any:
        """
        Send a reply to the same conversation.

        ```python
        await message.answer("Ответ!")
        await message.answer("С клавиатурой", keyboard=json.dumps(kb))
        ```
        """
        assert self._api is not None, "Message is not bound to an APIClient"
        return await self._api.messages.send(
            peer_id=self.peer_id,
            message=text,
            random_id=random.randint(0, 2**31),
            **kwargs,
        )

    async def reply(self, text: str, **kwargs: Any) -> Any:
        """
        Send a reply that quotes this message.

        ```python
        await message.reply("Получил!")
        ```
        """
        assert self._api is not None, "Message is not bound to an APIClient"
        return await self._api.messages.send(
            peer_id=self.peer_id,
            message=text,
            reply_to=self.id,
            random_id=random.randint(0, 2**31),
            **kwargs,
        )

    async def delete(self, *, delete_for_all: bool = False) -> Any:
        """Delete this message."""
        assert self._api is not None, "Message is not bound to an APIClient"
        return await self._api.messages.delete(
            message_ids=self.id,
            delete_for_all=int(delete_for_all),
        )

    @property
    def is_private(self) -> bool:
        """``True`` if this is a private message (not a chat or community)."""
        return 0 < self.peer_id < 2_000_000_000

    @property
    def is_chat(self) -> bool:
        """``True`` if this message is from a multi-user chat."""
        return self.peer_id > 2_000_000_000

    @property
    def chat_id(self) -> int | None:
        """Chat ID for multi-user chats, ``None`` otherwise."""
        return self.peer_id - 2_000_000_000 if self.is_chat else None
