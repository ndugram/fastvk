from __future__ import annotations


from typing import ClassVar

from fastvk.callback_data import CallbackData
from fastvk.filters.builtin import CallbackDataFilter, Command, Text, StateFilter
from fastvk.types.callback import CallbackQuery
from fastvk.filters.magic import F
from fastvk.fsm.context import FSMContext
from fastvk.fsm.state import State, StatesGroup
from fastvk.fsm.storage import MemoryStorage
from fastvk.types.command import CommandArgs


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


class TestCommandArgs:
    def test_injects_args_into_data(self) -> None:
        f = Command("ban")
        data: dict = {}
        f(_FakeMsg("/ban 123 спам"), data)
        assert CommandArgs in data
        assert data[CommandArgs].args == ("123", "спам")

    def test_injects_empty_args_for_bare_command(self) -> None:
        f = Command("start")
        data: dict = {}
        f(_FakeMsg("/start"), data)
        assert data[CommandArgs].args == ()
        assert data[CommandArgs].text == ""

    def test_text_preserves_full_arg_string(self) -> None:
        f = Command("say")
        data: dict = {}
        f(_FakeMsg("/say hello world"), data)
        assert data[CommandArgs].text == "hello world"

    def test_command_name_stored(self) -> None:
        f = Command("ping")
        data: dict = {}
        f(_FakeMsg("/ping"), data)
        assert data[CommandArgs].command == "ping"

    def test_strips_botname_mention(self) -> None:
        f = Command("start")
        data: dict = {}
        f(_FakeMsg("/start@mybot arg1"), data)
        assert data[CommandArgs].args == ("arg1",)

    def test_mention_no_args(self) -> None:
        f = Command("start")
        data: dict = {}
        f(_FakeMsg("/start@mybot"), data)
        assert data[CommandArgs].args == ()
        assert data[CommandArgs].text == ""

    def test_getitem(self) -> None:
        ca = CommandArgs(command="ban", args=("123", "спам"), text="123 спам")
        assert ca[0] == "123"
        assert ca[1] == "спам"

    def test_len(self) -> None:
        ca = CommandArgs(command="ban", args=("a", "b", "c"), text="a b c")
        assert len(ca) == 3

    def test_bool_true(self) -> None:
        ca = CommandArgs(command="ban", args=("123",), text="123")
        assert bool(ca) is True

    def test_bool_false(self) -> None:
        ca = CommandArgs(command="start", args=(), text="")
        assert bool(ca) is False

    def test_get_existing(self) -> None:
        ca = CommandArgs(command="ban", args=("123",), text="123")
        assert ca.get(0) == "123"

    def test_get_missing_returns_default(self) -> None:
        ca = CommandArgs(command="ban", args=("123",), text="123")
        assert ca.get(5, "default") == "default"

    def test_no_injection_on_no_match(self) -> None:
        f = Command("start")
        data: dict = {}
        f(_FakeMsg("/help"), data)
        assert CommandArgs not in data


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


def _make_cb(payload: dict) -> CallbackQuery:
    return CallbackQuery(
        user_id=1,
        peer_id=2,
        event_id="test",
        payload=payload,
        conversation_message_id=0,
    )


class TestCallbackDataFilter:
    def test_matches_and_injects(self) -> None:
        class BuyCb(CallbackData):
            prefix: ClassVar[str] = "buy"
            item_id: int

        f = CallbackDataFilter(BuyCb)
        cb = _make_cb({"item_id": 5})
        context: dict = {}
        assert f(cb, context) is True
        assert BuyCb in context
        assert context[BuyCb].item_id == 5

    def test_no_match_wrong_payload(self) -> None:
        class BuyCb(CallbackData):
            prefix: ClassVar[str] = "buy"
            item_id: int

        f = CallbackDataFilter(BuyCb)
        cb = _make_cb({"other": "data"})
        assert f(cb, {}) is False

    def test_no_match_non_callback_event(self) -> None:
        class BuyCb(CallbackData):
            prefix: ClassVar[str] = "buy"
            item_id: int

        f = CallbackDataFilter(BuyCb)
        msg = _FakeMsg("/start")
        assert f(msg, {}) is False

    def test_multiple_callback_types_isolated(self) -> None:
        class BuyCb(CallbackData):
            prefix: ClassVar[str] = "buy"
            item_id: int

        class VoteCb(CallbackData):
            prefix: ClassVar[str] = "vote"
            rating: int

        buy_filter = CallbackDataFilter(BuyCb)
        vote_filter = CallbackDataFilter(VoteCb)

        cb = _make_cb({"item_id": 1})
        ctx: dict = {}
        assert buy_filter(cb, ctx) is True
        assert vote_filter(cb, ctx) is False
        assert BuyCb in ctx
        assert VoteCb not in ctx

    def test_repr(self) -> None:
        class BuyCb(CallbackData):
            prefix: ClassVar[str] = "buy"
            item_id: int

        f = CallbackDataFilter(BuyCb)
        assert "BuyCb" in repr(f)


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
