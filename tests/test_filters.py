from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from fastvk.filters.builtin import Command, Text, StateFilter
from fastvk.filters.magic import F, MagicFilter
from fastvk.fsm.context import FSMContext
from fastvk.fsm.state import State, StatesGroup
from fastvk.fsm.storage import MemoryStorage
from fastvk.types.message import Message


class _FakeMsg:
    def __init__(self, text: str = "") -> None:
        self.text = text
        self.from_id = 123456


class TestCommand:
    def test_exact_command(self) -> None:
        f = Command("start")
        msg = _FakeMsg("/start")
        assert f(msg, {}) is True

    def test_command_with_argument(self) -> None:
        f = Command("ban")
        msg = _FakeMsg("/ban 123456")
        assert f(msg, {}) is True

    def test_command_with_mention(self) -> None:
        f = Command("start")
        msg = _FakeMsg("/start@mybot")
        assert f(msg, {}) is True

    def test_wrong_command(self) -> None:
        f = Command("start")
        msg = _FakeMsg("/help")
        assert f(msg, {}) is False

    def test_empty_text(self) -> None:
        f = Command("start")
        msg = _FakeMsg("")
        assert f(msg, {}) is False

    def test_multiple_commands(self) -> None:
        f = Command("start", "help", "menu")
        assert f(_FakeMsg("/start"), {}) is True
        assert f(_FakeMsg("/help"), {}) is True
        assert f(_FakeMsg("/menu"), {}) is True
        assert f(_FakeMsg("/other"), {}) is False

    def test_leading_slash_stripped_from_init(self) -> None:
        f = Command("/start")
        assert f(_FakeMsg("/start"), {}) is True

    def test_not_a_command(self) -> None:
        f = Command("start")
        assert f(_FakeMsg("start"), {}) is False

    def test_repr(self) -> None:
        f = Command("start")
        assert "Command" in repr(f)


class TestText:
    def test_exact_match(self) -> None:
        f = Text("привет")
        assert f(_FakeMsg("привет"), {}) is True

    def test_exact_match_case_insensitive(self) -> None:
        f = Text("ПРИВЕТ")
        assert f(_FakeMsg("привет"), {}) is True

    def test_exact_match_case_sensitive_fails(self) -> None:
        f = Text("ПРИВЕТ", ignore_case=False)
        assert f(_FakeMsg("привет"), {}) is False

    def test_no_exact_match(self) -> None:
        f = Text("привет")
        assert f(_FakeMsg("пока"), {}) is False

    def test_contains(self) -> None:
        f = Text("вет", contains=True)
        assert f(_FakeMsg("привет"), {}) is True

    def test_contains_not_present(self) -> None:
        f = Text("xyz", contains=True)
        assert f(_FakeMsg("привет"), {}) is False

    def test_multiple_texts(self) -> None:
        f = Text("да", "нет", "может")
        assert f(_FakeMsg("да"), {}) is True
        assert f(_FakeMsg("нет"), {}) is True
        assert f(_FakeMsg("может"), {}) is True
        assert f(_FakeMsg("возможно"), {}) is False

    def test_empty_text(self) -> None:
        f = Text("привет")
        assert f(_FakeMsg(""), {}) is False

    def test_repr(self) -> None:
        f = Text("привет")
        assert "Text" in repr(f)


class TestStateFilter:
    async def test_matches_current_state(self) -> None:
        class Form(StatesGroup):
            waiting = State()

        storage = MemoryStorage()
        ctx = FSMContext(storage, peer_id=1, user_id=1)
        await ctx.set_state(Form.waiting)

        f = StateFilter(Form.waiting)
        msg = _FakeMsg("test")
        result = await f(msg, {FSMContext: ctx})
        assert result is True

    async def test_no_match_different_state(self) -> None:
        class Form(StatesGroup):
            state_a = State()
            state_b = State()

        storage = MemoryStorage()
        ctx = FSMContext(storage, peer_id=1, user_id=1)
        await ctx.set_state(Form.state_a)

        f = StateFilter(Form.state_b)
        result = await f(_FakeMsg(), {FSMContext: ctx})
        assert result is False

    async def test_no_state_set(self) -> None:
        class Form(StatesGroup):
            waiting = State()

        storage = MemoryStorage()
        ctx = FSMContext(storage, peer_id=1, user_id=1)

        f = StateFilter(Form.waiting)
        result = await f(_FakeMsg(), {FSMContext: ctx})
        assert result is False


class TestF:
    def test_attr_equals(self) -> None:
        f = F.text == "привет"
        msg = _FakeMsg("привет")
        assert f(msg, {}) is True

    def test_attr_equals_false(self) -> None:
        f = F.text == "привет"
        msg = _FakeMsg("пока")
        assert f(msg, {}) is False

    def test_attr_in(self) -> None:
        f = F.from_id.in_(1, 2, 3)
        msg = _FakeMsg()
        msg.from_id = 2  # type: ignore[assignment]
        assert f(msg, {}) is True

    def test_attr_not_in(self) -> None:
        f = F.from_id.in_(1, 2, 3)
        msg = _FakeMsg()
        msg.from_id = 99  # type: ignore[assignment]
        assert f(msg, {}) is False

    def test_attr_contains(self) -> None:
        f = F.text.contains("вет")
        msg = _FakeMsg("привет")
        assert f(msg, {}) is True

    def test_attr_not_contains(self) -> None:
        f = F.text.contains("xyz")
        msg = _FakeMsg("привет")
        assert f(msg, {}) is False
