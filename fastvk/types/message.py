from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..api.client import Bot
    from ..keyboard import Keyboard


@dataclass(slots=True)
class Message:
    """
    Incoming VK message.

    ```python
    @router.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer("Привет!")
    ```
    """

    id: int
    date: int
    peer_id: int
    from_id: int
    text: str
    attachments: list[dict] = field(default_factory=list)
    reply_message: dict | None = None
    fwd_messages: list[dict] = field(default_factory=list)
    payload: str | None = None
    raw: dict = field(default_factory=dict)
    _bot: Bot | None = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: dict, bot: Bot) -> Message:
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
            _bot=bot,
        )

    async def answer(
        self,
        text: str,
        *,
        keyboard: Keyboard | str | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Send a message to the same conversation.

        ```python
        await message.answer("Привет!")
        await message.answer(
            "Выбери:",
            keyboard=Keyboard().row(Button.text("Ок", color="primary")),
        )
        await message.answer("Убрать кнопки", keyboard=Keyboard.remove())
        ```
        """
        assert self._bot is not None
        if keyboard is not None:
            kwargs["keyboard"] = str(keyboard)
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
        """Send a reply that quotes this message."""
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
        """Delete this message."""
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
