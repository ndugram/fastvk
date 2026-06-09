from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from fastvk.exceptions import VKAPIError
from fastvk.fsm.context import FSMContext
from fastvk.fsm.storage import MemoryStorage
from fastvk.filters.builtin import Command, Text
from fastvk.router import Router, _get_params, _resolve_kwargs
from fastvk.types.message import Message
from fastvk.types.update import Update
from fastvk.types.user import User


class TestHandlerRegistration:
    def test_message_registers_handler(self) -> None:
        router = Router()

        @router.message()
        async def handler(message: Message) -> None: ...

        assert len(router._handlers) == 1
        assert router._handlers[0].event_type == "message_new"
        assert router._handlers[0].callback is handler

    def test_callback_registers_handler(self) -> None:
        router = Router()

        @router.callback()
        async def handler() -> None: ...

        assert router._handlers[0].event_type == "message_event"

    def test_on_registers_custom_event(self) -> None:
        router = Router()

        @router.on("photo_new")
        async def handler() -> None: ...

        assert router._handlers[0].event_type == "photo_new"

    def test_multiple_handlers_registered(self) -> None:
        router = Router()

        @router.message()
        async def h1(message: Message) -> None: ...

        @router.message(Command("start"))
        async def h2(message: Message) -> None: ...

        assert len(router._handlers) == 2

    def test_filters_stored_on_handler(self) -> None:
        router = Router()
        cmd = Command("ping")

        @router.message(cmd)
        async def handler(message: Message) -> None: ...

        assert len(router._handlers[0].filters) == 1

    def test_include_router_collects_handlers(self) -> None:
        parent = Router()
        child = Router()

        @child.message()
        async def handler(message: Message) -> None: ...

        parent.include_router(child)
        all_handlers = parent._collect_all_handlers()

        assert len(all_handlers) == 1
        assert all_handlers[0].callback is handler

    def test_nested_routers_collected(self) -> None:
        root = Router()
        mid = Router()
        leaf = Router()

        @leaf.message()
        async def h1(message: Message) -> None: ...

        @mid.message()
        async def h2(message: Message) -> None: ...

        mid.include_router(leaf)
        root.include_router(mid)

        all_handlers = root._collect_all_handlers()
        assert len(all_handlers) == 2

    def test_exception_handler_registered(self) -> None:
        router = Router()

        @router.exception_handler(VKAPIError)
        async def on_error(error: VKAPIError) -> None: ...

        assert len(router._error_handlers) == 1
        assert router._error_handlers[0].exc_types == (VKAPIError,)

    def test_exception_handler_no_types_defaults_to_exception(self) -> None:
        router = Router()

        @router.exception_handler()
        async def on_error(error: Exception) -> None: ...

        assert router._error_handlers[0].exc_types == (Exception,)


class TestFeedUpdate:
    async def test_dispatches_message_new(self, mock_bot: MagicMock, make_update: Any, storage: MemoryStorage) -> None:
        router = Router()
        called_with: list[Message] = []

        @router.message()
        async def handler(message: Message) -> None:
            called_with.append(message)

        update = make_update("message_new")
        handled = await router.feed_update(update, mock_bot, storage)

        assert handled is True
        assert len(called_with) == 1
        assert isinstance(called_with[0], Message)

    async def test_dispatches_to_sub_router(self, mock_bot: MagicMock, make_update: Any, storage: MemoryStorage) -> None:
        parent = Router()
        child = Router()
        called: list[bool] = []

        @child.message()
        async def handler(message: Message) -> None:
            called.append(True)

        parent.include_router(child)
        update = make_update("message_new")
        handled = await parent.feed_update(update, mock_bot, storage)

        assert handled is True
        assert called == [True]

    async def test_no_matching_handler_returns_false(self, mock_bot: MagicMock, make_update: Any, storage: MemoryStorage) -> None:
        router = Router()
        update = make_update("message_new")
        handled = await router.feed_update(update, mock_bot, storage)

        assert handled is False

    async def test_filter_blocks_non_matching_message(self, mock_bot: MagicMock, make_update: Any, storage: MemoryStorage) -> None:
        router = Router()
        called: list[bool] = []

        @router.message(Command("start"))
        async def handler(message: Message) -> None:
            called.append(True)

        update = make_update("message_new", obj={
            "message": {"id": 1, "date": 1700000000, "peer_id": 1, "from_id": 1, "text": "не команда"}
        })
        handled = await router.feed_update(update, mock_bot, storage)

        assert handled is False
        assert called == []

    async def test_filter_passes_matching_message(self, mock_bot: MagicMock, make_update: Any, storage: MemoryStorage) -> None:
        router = Router()
        called: list[bool] = []

        @router.message(Command("start"))
        async def handler(message: Message) -> None:
            called.append(True)

        update = make_update("message_new", obj={
            "message": {"id": 1, "date": 1700000000, "peer_id": 1, "from_id": 1, "text": "/start"}
        })
        handled = await router.feed_update(update, mock_bot, storage)

        assert handled is True
        assert called == [True]

    async def test_injects_fsm_context(self, mock_bot: MagicMock, make_update: Any, storage: MemoryStorage) -> None:
        router = Router()
        injected: list[FSMContext] = []

        @router.message()
        async def handler(state: FSMContext) -> None:
            injected.append(state)

        update = make_update("message_new")
        await router.feed_update(update, mock_bot, storage)

        assert len(injected) == 1
        assert isinstance(injected[0], FSMContext)

    async def test_injects_user(self, mock_bot: MagicMock, make_update: Any, storage: MemoryStorage) -> None:
        router = Router()
        injected: list[User] = []

        @router.message()
        async def handler(user: User) -> None:
            injected.append(user)

        update = make_update("message_new")
        await router.feed_update(update, mock_bot, storage)

        assert injected[0].first_name == "Иван"

    async def test_message_from_user_set(self, mock_bot: MagicMock, make_update: Any, storage: MemoryStorage) -> None:
        router = Router()
        messages: list[Message] = []

        @router.message()
        async def handler(message: Message) -> None:
            messages.append(message)

        update = make_update("message_new")
        await router.feed_update(update, mock_bot, storage)

        assert messages[0].from_user is not None
        assert messages[0].from_user.id == 123456

    async def test_exception_handler_catches_error(self, mock_bot: MagicMock, make_update: Any, storage: MemoryStorage) -> None:
        router = Router()
        errors: list[Exception] = []

        @router.message()
        async def handler(message: Message) -> None:
            raise ValueError("boom")

        @router.exception_handler(ValueError)
        async def on_error(error: ValueError) -> None:
            errors.append(error)

        update = make_update("message_new")
        handled = await router.feed_update(update, mock_bot, storage)

        assert handled is True
        assert len(errors) == 1
        assert str(errors[0]) == "boom"

    async def test_unhandled_exception_reraises(self, mock_bot: MagicMock, make_update: Any, storage: MemoryStorage) -> None:
        router = Router()

        @router.message()
        async def handler(message: Message) -> None:
            raise RuntimeError("unhandled")

        update = make_update("message_new")
        with pytest.raises(RuntimeError, match="unhandled"):
            await router.feed_update(update, mock_bot, storage)

    async def test_dispatches_message_event(self, mock_bot: MagicMock, storage: MemoryStorage) -> None:
        router = Router()
        called: list[bool] = []

        @router.callback()
        async def handler() -> None:
            called.append(True)

        update = Update(
            type="message_event",
            object={
                "user_id": 1,
                "peer_id": 1,
                "event_id": "e1",
                "payload": "{}",
                "conversation_message_id": 1,
            },
            group_id=1,
            event_id="e1",
        )
        handled = await router.feed_update(update, mock_bot, storage)

        assert handled is True
        assert called == [True]


class TestDI:
    def test_get_params_returns_name_and_hint(self) -> None:
        async def handler(message: Message, state: FSMContext) -> None: ...

        params = _get_params(handler)
        names = [p[0] for p in params]
        types = [p[1] for p in params]

        assert "message" in names
        assert "state" in names
        assert Message in types
        assert FSMContext in types

    def test_resolve_kwargs_exact_type(self) -> None:
        async def handler(message: Message) -> None: ...

        msg = MagicMock(spec=Message)
        context: dict = {Message: msg}
        kwargs = _resolve_kwargs(handler, context)

        assert kwargs["message"] is msg

    def test_resolve_kwargs_multiple_types(self) -> None:
        async def handler(message: Message, state: FSMContext) -> None: ...

        msg = MagicMock(spec=Message)
        ctx = MagicMock(spec=FSMContext)
        context: dict = {Message: msg, FSMContext: ctx}
        kwargs = _resolve_kwargs(handler, context)

        assert kwargs["message"] is msg
        assert kwargs["state"] is ctx

    def test_resolve_kwargs_skips_unannotated(self) -> None:
        async def handler(message, state: FSMContext) -> None: ...  # type: ignore[misc]

        ctx = MagicMock(spec=FSMContext)
        context: dict = {FSMContext: ctx}
        kwargs = _resolve_kwargs(handler, context)

        assert "message" not in kwargs
        assert kwargs["state"] is ctx
