from __future__ import annotations

import json
from typing import Any, Literal, Union

from .enums.color import Color

ButtonColor = Union[Color, str]
ButtonDict = dict[str, Any]


class Button:
    """Factory for VK keyboard button dicts.

    ```python
    Button.text("Привет", color="primary")
    Button.callback("Нажми", payload={"cmd": "click"})
    Button.link("GitHub", url="https://github.com")
    Button.location()
    ```
    """

    @staticmethod
    def text(
        label: str,
        *,
        color: ButtonColor = "secondary",
        payload: dict[str, Any] | str | None = None,
    ) -> ButtonDict:
        """Text button — appears on regular keyboard."""
        action: dict[str, Any] = {"type": "text", "label": label}
        if payload is not None:
            action["payload"] = json.dumps(payload, ensure_ascii=False) if isinstance(payload, dict) else payload
        return {"action": action, "color": color}

    @staticmethod
    def callback(
        label: str,
        *,
        payload: dict[str, Any] | str | None = None,
    ) -> ButtonDict:
        """Callback button — triggers ``message_event`` on inline keyboard."""
        action: dict[str, Any] = {"type": "callback", "label": label}
        if payload is not None:
            action["payload"] = json.dumps(payload, ensure_ascii=False) if isinstance(payload, dict) else payload
        return {"action": action}

    @staticmethod
    def link(
        label: str,
        url: str,
        *,
        payload: dict[str, Any] | str | None = None,
    ) -> ButtonDict:
        """Button that opens a URL."""
        action: dict[str, Any] = {"type": "open_link", "label": label, "link": url}
        if payload is not None:
            action["payload"] = json.dumps(payload, ensure_ascii=False) if isinstance(payload, dict) else payload
        return {"action": action}

    @staticmethod
    def location() -> ButtonDict:
        """Button that requests the user's location."""
        return {"action": {"type": "location"}}

    @staticmethod
    def vkpay(
        *,
        action: Literal["pay-to-group", "transfer-to-group", "transfer-to-user"] = "pay-to-group",
        group_id: int | None = None,
        user_id: int | None = None,
        amount: int | None = None,
        description: str = "",
        merchant_id: int | None = None,
        aid: int | None = None,
    ) -> ButtonDict:
        """
        VK Pay button. Builds the ``hash`` parameter from typed arguments.

        ```python
        # Payment to group
        Button.vkpay(action="pay-to-group", group_id=123, amount=100, description="Оплата")

        # Transfer to group
        Button.vkpay(action="transfer-to-group", group_id=123, aid=1)

        # Transfer to user
        Button.vkpay(action="transfer-to-user", user_id=456, aid=1)
        ```
        """
        params: dict[str, Any] = {"action": action}
        if group_id is not None:
            params["group_id"] = group_id
        if user_id is not None:
            params["user_id"] = user_id
        if amount is not None:
            params["amount"] = amount
        if description:
            params["description"] = description
        if merchant_id is not None:
            params["merchant_id"] = merchant_id
        if aid is not None:
            params["aid"] = aid
        hash_str = "&".join(f"{k}={v}" for k, v in params.items())
        return {"action": {"type": "vkpay", "hash": hash_str}}


class Keyboard:
    """Builder for VK keyboards — regular and inline.

    ```python
    # Regular keyboard
    kb = (
        Keyboard(one_time=True)
        .row(Button.text("✅ Да", color="positive"), Button.text("❌ Нет", color="negative"))
        .row(Button.text("Отмена"))
    )
    await message.answer("Выбери:", keyboard=kb)

    # Inline keyboard (callback buttons)
    kb = (
        Keyboard(inline=True)
        .row(Button.callback("👍", payload={"v": 1}), Button.callback("👎", payload={"v": 0}))
    )
    await message.answer("Оцени:", keyboard=kb)
    ```
    """

    def __init__(self, *, one_time: bool = False, inline: bool = False) -> None:
        self._rows: list[list[ButtonDict]] = []
        self._one_time = one_time
        self._inline = inline

    def row(self, *buttons: ButtonDict) -> Keyboard:
        """Append a new row with *buttons*."""
        self._rows.append(list(buttons))
        return self

    def add(self, *buttons: ButtonDict) -> Keyboard:
        """Append *buttons* to the last row (creates a row if none exist)."""
        if not self._rows:
            self._rows.append([])
        self._rows[-1].extend(buttons)
        return self

    def build(self) -> str:
        """Serialize to JSON string for VK API ``keyboard`` parameter."""
        return json.dumps(
            {"one_time": self._one_time, "inline": self._inline, "buttons": self._rows},
            ensure_ascii=False,
        )

    def __str__(self) -> str:
        return self.build()

    @staticmethod
    def remove() -> str:
        """JSON string that removes the keyboard from the chat."""
        return json.dumps({"buttons": [], "one_time": True})
