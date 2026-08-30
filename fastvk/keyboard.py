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
    def vkapps(
        label: str,
        *,
        app_id: int,
        owner_id: int | None = None,
        hash: str = "",
        payload: dict[str, Any] | str | None = None,
    ) -> ButtonDict:
        """Button that opens a VK Mini App."""
        action: dict[str, Any] = {
            "type": "open_app",
            "label": label,
            "app_id": app_id,
            "hash": hash,
        }
        if owner_id is not None:
            action["owner_id"] = owner_id
        if payload is not None:
            action["payload"] = (
                json.dumps(payload, ensure_ascii=False)
                if isinstance(payload, dict)
                else payload
            )
        return {"action": action}

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


class Carousel:
    """Builder for VK message carousel templates (``template`` API parameter).

    ```python
    carousel = (
        Carousel()
        .element(
            title="Товар 1",
            description="99 ₽",
            photo_id="-1_2",
            buttons=[Button.callback("Купить", payload={"buy": 1})],
            link="https://example.com/1",
        )
        .element(title="Товар 2", buttons=[Button.callback("Купить", payload={"buy": 2})])
    )
    await bot.messages.send(peer_id=1, message="Каталог", template=str(carousel), random_id=0)
    ```
    """

    def __init__(self) -> None:
        self._elements: list[dict[str, Any]] = []

    def element(
        self,
        *,
        title: str = "",
        description: str = "",
        photo_id: str | None = None,
        buttons: list[ButtonDict] | None = None,
        link: str | None = None,
    ) -> Carousel:
        """Append one card. ``link`` sets an ``open_link`` tap action for the card."""
        if len(self._elements) >= 10:
            raise ValueError("a carousel holds at most 10 elements")
        el: dict[str, Any] = {"buttons": buttons or []}
        if title:
            el["title"] = title
        if description:
            el["description"] = description
        if photo_id is not None:
            el["photo_id"] = photo_id
        el["action"] = (
            {"type": "open_link", "link": link}
            if link is not None
            else {"type": "open_photo"}
        )
        self._elements.append(el)
        return self

    def build(self) -> str:
        return json.dumps(
            {"type": "carousel", "elements": self._elements}, ensure_ascii=False
        )

    def __str__(self) -> str:
        return self.build()
