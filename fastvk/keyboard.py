from __future__ import annotations

import json
from typing import Any, Union

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
