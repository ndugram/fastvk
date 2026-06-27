from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from ..callback_data import CallbackData
from ..fsm.context import FSMContext
from ..fsm.state import State
from ..types.callback import CallbackQuery
from ..types.command import CommandArgs
from ..types.message import Message


class Command:
    """
    Filter that matches messages starting with a bot command.

    Handles ``/cmd``, ``/cmd@botname``, and ``/cmd argument`` forms.
    Custom prefixes are supported via *prefix*.

    ```python
    @router.message(Command("start", "help"))
    async def on_start(message: Message) -> None:
        await message.answer("Привет!")

    # also matches !ban and !kick
    @router.message(Command("ban", "kick", prefix="!/"))
    async def on_mod(message: Message) -> None: ...
    ```
    """

    def __init__(self, *commands: str, prefix: str = "/") -> None:
        self.prefix = prefix
        self.commands = {cmd.lstrip(prefix) for cmd in commands}

    def __call__(self, message: Message, data: dict) -> bool:
        if not message.text:
            return False
        text = message.text.strip()
        for p in self.prefix:
            for cmd in self.commands:
                if text == f"{p}{cmd}":
                    data[CommandArgs] = CommandArgs(command=cmd, args=(), text="")
                    return True
                if text.startswith(f"{p}{cmd} ") or text.startswith(f"{p}{cmd}@"):
                    rest = text[len(p) + len(cmd) :]
                    if rest.startswith("@"):
                        rest = rest.split(" ", 1)[1] if " " in rest else ""
                    arg_text = rest.strip()
                    data[CommandArgs] = CommandArgs(
                        command=cmd,
                        args=tuple(arg_text.split()),
                        text=arg_text,
                    )
                    return True
        return False

    def __repr__(self) -> str:
        return f"Command({', '.join(self.commands)!r}, prefix={self.prefix!r})"


class CommandStart(Command):
    """Shortcut for ``Command("start")``."""

    def __init__(self) -> None:
        super().__init__("start")


class CommandHelp(Command):
    """Shortcut for ``Command("help")``."""

    def __init__(self) -> None:
        super().__init__("help")


class Text:
    """
    Filter that matches message text by exact value or substring.

    ```python
    @router.message(Text("привет"))
    async def on_hello(message: Message) -> None:
        await message.answer("И тебе привет!")

    @router.message(Text("help", contains=True, ignore_case=True))
    async def on_help_mention(message: Message) -> None:
        await message.answer("Нужна помощь?")
    ```
    """

    def __init__(
        self,
        *texts: str,
        contains: bool = False,
        ignore_case: bool = True,
    ) -> None:
        self.texts = texts
        self.contains = contains
        self.ignore_case = ignore_case

    def __call__(self, message: Message, data: dict) -> bool:
        if not message.text:
            return False
        msg = message.text.lower() if self.ignore_case else message.text
        for t in self.texts:
            cmp = t.lower() if self.ignore_case else t
            if self.contains and cmp in msg:
                return True
            if not self.contains and msg == cmp:
                return True
        return False

    def __repr__(self) -> str:
        return f"Text({self.texts!r}, contains={self.contains})"


class StateFilter:
    """
    Filter that matches the user's current FSM state.

    ```python
    @router.message(StateFilter(Form.waiting_name))
    async def got_name(message: Message, state: FSMContext) -> None:
        await state.update_data(name=message.text)
    ```

    Pass ``None`` to match users with no active state:

    ```python
    @router.message(StateFilter(None))
    async def no_state(message: Message) -> None: ...
    ```
    """

    def __init__(self, *states: State | str | None) -> None:
        self._states: list[str | None] = []
        for s in states:
            if isinstance(s, State):
                self._states.append(s.state)
            else:
                self._states.append(s)

    async def __call__(self, message: Message, data: dict) -> bool:
        ctx: FSMContext | None = data.get(FSMContext)
        current = await ctx.get_state() if ctx is not None else None
        return current in self._states

    def __repr__(self) -> str:
        return f"StateFilter({self._states!r})"


class FromUser:
    """
    Filter that only allows messages from specific user IDs.

    ```python
    ADMIN_ID = 123456789

    @router.message(FromUser(ADMIN_ID), Command("ban"))
    async def admin_ban(message: Message) -> None: ...
    ```
    """

    def __init__(self, *user_ids: int) -> None:
        self.user_ids = frozenset(user_ids)

    def __call__(self, message: Message, data: dict) -> bool:
        return message.from_id in self.user_ids

    def __repr__(self) -> str:
        return f"FromUser({set(self.user_ids)!r})"


class IsChat:
    """
    Filter that restricts handlers to a specific chat type.

    ```python
    @router.message(IsChat("private"))
    async def private_only(message: Message) -> None: ...

    @router.message(IsChat("chat"))
    async def chat_only(message: Message) -> None: ...
    ```

    Accepted values: ``"private"``, ``"chat"``.
    """

    _PRIVATE = "private"
    _CHAT = "chat"

    def __init__(self, *types: str) -> None:
        self.types = frozenset(types)

    def __call__(self, message: Message, data: dict) -> bool:
        if self._PRIVATE in self.types and message.is_private:
            return True
        if self._CHAT in self.types and message.is_chat:
            return True
        return False

    def __repr__(self) -> str:
        return f"IsChat({set(self.types)!r})"


class CallbackDataFilter:
    """
    Filter that matches callbacks by :class:`~fastvk.CallbackData` type.

    Automatically unpacks the payload and injects the typed object
    into the handler via dependency injection.

    Usage:
        class BuyCallback(CallbackData):
            prefix: ClassVar[str] = "buy"
            item_id: int

        @bot.callback(CallbackDataFilter(BuyCallback))
        async def on_buy(
            callback: CallbackQuery,
            callback_data: BuyCallback,   # injected automatically
        ) -> None:
            await callback.answer(f"Item #{callback_data.item_id}")
    """

    def __init__(self, callback_data_cls: type[CallbackData]) -> None:
        self._callback_data_cls = callback_data_cls

    def __call__(self, event: Any, context: dict) -> bool:
        if not isinstance(event, CallbackQuery):
            return False
        try:
            cb = self._callback_data_cls.unpack(event.payload)
        except (ValidationError, TypeError, json.JSONDecodeError):
            return False
        context[self._callback_data_cls] = cb
        return True

    def __repr__(self) -> str:
        return f"CallbackDataFilter({self._callback_data_cls.__name__})"


def _normalize_filter(f: Any) -> Any:
    """Wrap a bare :class:`~fastvk.fsm.State` in a :class:`StateFilter`."""
    if isinstance(f, State):
        return StateFilter(f)
    return f
