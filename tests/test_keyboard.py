from __future__ import annotations

import json

import pytest

from fastvk.keyboard import Button, Keyboard
from fastvk.enums.color import Color


class TestButton:
    def test_text_button_structure(self) -> None:
        btn = Button.text("Нажми меня")
        assert btn["action"]["type"] == "text"
        assert btn["action"]["label"] == "Нажми меня"
        assert btn["color"] == "secondary"

    def test_text_button_with_color(self) -> None:
        btn = Button.text("Да", color=Color.POSITIVE)
        assert btn["color"] == Color.POSITIVE

    def test_text_button_with_dict_payload(self) -> None:
        btn = Button.text("Ok", payload={"cmd": "ok"})
        payload_str = btn["action"]["payload"]
        assert json.loads(payload_str) == {"cmd": "ok"}

    def test_text_button_with_string_payload(self) -> None:
        btn = Button.text("Ok", payload='{"cmd": "ok"}')
        assert btn["action"]["payload"] == '{"cmd": "ok"}'

    def test_text_button_no_payload(self) -> None:
        btn = Button.text("No payload")
        assert "payload" not in btn["action"]

    def test_callback_button_structure(self) -> None:
        btn = Button.callback("Кликни", payload={"v": 1})
        assert btn["action"]["type"] == "callback"
        assert btn["action"]["label"] == "Кликни"
        assert "color" not in btn

    def test_link_button_structure(self) -> None:
        btn = Button.link("GitHub", url="https://github.com")
        assert btn["action"]["type"] == "open_link"
        assert btn["action"]["link"] == "https://github.com"
        assert btn["action"]["label"] == "GitHub"

    def test_location_button_structure(self) -> None:
        btn = Button.location()
        assert btn["action"]["type"] == "location"


class TestKeyboard:
    def test_row_appends_row(self) -> None:
        kb = Keyboard()
        kb.row(Button.text("A"), Button.text("B"))
        data = json.loads(kb.build())
        assert len(data["buttons"]) == 1
        assert len(data["buttons"][0]) == 2

    def test_multiple_rows(self) -> None:
        kb = (
            Keyboard()
            .row(Button.text("Row 1"))
            .row(Button.text("Row 2"))
        )
        data = json.loads(kb.build())
        assert len(data["buttons"]) == 2

    def test_add_to_last_row(self) -> None:
        kb = Keyboard()
        kb.row(Button.text("A"))
        kb.add(Button.text("B"))
        data = json.loads(kb.build())
        assert len(data["buttons"]) == 1
        assert len(data["buttons"][0]) == 2

    def test_add_creates_row_if_empty(self) -> None:
        kb = Keyboard()
        kb.add(Button.text("A"))
        data = json.loads(kb.build())
        assert len(data["buttons"]) == 1

    def test_one_time_flag(self) -> None:
        kb = Keyboard(one_time=True)
        data = json.loads(kb.build())
        assert data["one_time"] is True

    def test_inline_flag(self) -> None:
        kb = Keyboard(inline=True)
        data = json.loads(kb.build())
        assert data["inline"] is True

    def test_defaults(self) -> None:
        kb = Keyboard()
        data = json.loads(kb.build())
        assert data["one_time"] is False
        assert data["inline"] is False

    def test_str_equals_build(self) -> None:
        kb = Keyboard().row(Button.text("X"))
        assert str(kb) == kb.build()

    def test_remove_returns_empty_keyboard_json(self) -> None:
        data = json.loads(Keyboard.remove())
        assert data["buttons"] == []
        assert data["one_time"] is True

    def test_chaining_returns_same_instance(self) -> None:
        kb = Keyboard()
        result = kb.row(Button.text("A"))
        assert result is kb

    def test_build_is_valid_json(self) -> None:
        kb = (
            Keyboard(one_time=True)
            .row(Button.text("Да", color=Color.POSITIVE), Button.text("Нет", color=Color.NEGATIVE))
        )
        parsed = json.loads(kb.build())
        assert isinstance(parsed, dict)
        assert "buttons" in parsed
