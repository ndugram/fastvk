from __future__ import annotations

import json
from typing import TypeVar

from pydantic import BaseModel

C = TypeVar("C", bound="CallbackData")


class CallbackData(BaseModel):
    """Base class for callback data factories.

    Define a subclass with a ``prefix`` (class variable) and typed fields.
    Use ``.pack()`` to produce a payload string for ``Button.callback()``,
    and ``.unpack()`` to restore the object from a ``CallbackQuery.payload``.

    Usage:
        class BuyCallback(CallbackData):
            prefix = "buy"
            item_id: int
            count: int = 1

        # pack
        cb = BuyCallback(item_id=5, count=2)
        payload = cb.pack()
        Button.callback("Buy", payload=payload)

        # unpack
        @bot.callback()
        async def on_buy(callback: CallbackQuery) -> None:
            cb = BuyCallback.unpack(callback.payload)
            await callback.answer(f"Bought {cb.count}x item #{cb.item_id}")
    """

    def pack(self) -> str:
        data = self.model_dump(exclude_none=True)
        return f"{self.__class__.prefix}:{json.dumps(data, ensure_ascii=False, separators=(',', ':'))}" # type: ignore

    @classmethod
    def unpack(cls: type[C], value: str | dict) -> C:
        if isinstance(value, dict):
            return cls(**value)
        if isinstance(value, str):
            json_str = value.split(":", 1)[1] if ":" in value else value
            return cls(**json.loads(json_str))
        raise TypeError(f"Expected str or dict, got {type(value).__name__}")
