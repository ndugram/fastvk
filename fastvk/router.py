from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .filters.builtin import _normalize_filter
from .types.message import Message
from .types.update import Update

if TYPE_CHECKING:
    from .api.client import APIClient
    from .fsm.context import FSMContext
    from .fsm.storage import BaseStorage


@dataclass(frozen=True, slots=True)
class _HandlerDef:
    """Unresolved handler stored on :class:`Router` before an update arrives."""

    callback: Callable
    filters: tuple[Callable, ...]
    event_type: str


@dataclass(slots=True)
class _IncludeDef:
    """Represents a deferred ``include_router()`` call."""

    router: Router


async def _run_filter(f: Callable, event: Any, data: dict) -> bool:
    result = f(event, data)
    if asyncio.iscoroutine(result):
        result = await result
    return bool(result)


async def _call_handler(handler: Callable, data: dict) -> Any:
    """Inject handler parameters by name from *data*, then call it."""
    sig = inspect.signature(handler)
    kwargs: dict[str, Any] = {}

    for param_name, param in sig.parameters.items():
        if param_name in data:
            kwargs[param_name] = data[param_name]
        elif param.annotation is not inspect.Parameter.empty:
            ann = param.annotation
            for val in data.values():
                if isinstance(val, ann):
                    kwargs[param_name] = val
                    break

    if inspect.iscoroutinefunction(handler):
        return await handler(**kwargs)
    return handler(**kwargs)


class Router:
    """
    Groups related event handlers — analogous to aiogram's ``Router``
    and FastAPI's ``APIRouter``.

    ```python
    router = Router()

    @router.message(Command("start"))
    async def start(message: Message, state: FSMContext) -> None:
        await message.answer("Привет!")

    bot.include_router(router)
    ```
    """

    def __init__(self) -> None:
        self._handlers: list[_HandlerDef] = []
        self._sub_routers: list[_IncludeDef] = []

    def include_router(self, router: Router) -> None:
        """Mount *router* as a child — its handlers are checked after this router's."""
        self._sub_routers.append(_IncludeDef(router=router))

    def _register(
        self,
        event_type: str,
        *filters: Callable,
    ) -> Callable[[Callable], Callable]:
        def decorator(func: Callable) -> Callable:
            normalized = tuple(_normalize_filter(f) for f in filters)
            self._handlers.append(
                _HandlerDef(
                    callback=func,
                    filters=normalized,
                    event_type=event_type,
                )
            )
            return func

        return decorator

    def message(self, *filters: Callable) -> Callable[[Callable], Callable]:
        """
        Register a handler for ``message_new`` events.

        ```python
        @router.message(Command("ping"))
        async def ping(message: Message) -> None:
            await message.answer("pong")
        ```

        Pass no filters to catch all incoming messages:

        ```python
        @router.message()
        async def echo(message: Message) -> None:
            await message.answer(message.text)
        ```
        """
        return self._register("message_new", *filters)

    def message_reply(self, *filters: Callable) -> Callable[[Callable], Callable]:
        """Register a handler for ``message_reply`` events."""
        return self._register("message_reply", *filters)

    def message_allow(self, *filters: Callable) -> Callable[[Callable], Callable]:
        """Register a handler for ``message_allow`` (newsletter opt-in) events."""
        return self._register("message_allow", *filters)

    def group_join(self, *filters: Callable) -> Callable[[Callable], Callable]:
        """Register a handler fired when a user joins the group."""
        return self._register("group_join", *filters)

    def group_leave(self, *filters: Callable) -> Callable[[Callable], Callable]:
        """Register a handler fired when a user leaves the group."""
        return self._register("group_leave", *filters)

    def wall_post_new(self, *filters: Callable) -> Callable[[Callable], Callable]:
        """Register a handler for new wall posts."""
        return self._register("wall_post_new", *filters)

    def on(self, event_type: str, *filters: Callable) -> Callable[[Callable], Callable]:
        """
        Register a handler for any VK event type by name.

        ```python
        @router.on("photo_new")
        async def new_photo(event: dict, api: APIClient) -> None:
            print(event)
        ```
        """
        return self._register(event_type, *filters)

    async def feed_update(
        self,
        update: Update,
        api: APIClient,
        storage: BaseStorage,
    ) -> bool:
        """
        Dispatch *update* to the first matching handler.

        Returns ``True`` if a handler was found and called, ``False`` otherwise.
        """
        data: dict[str, Any] = {"api": api, "update": update, "event": update.object}

        if update.type == "message_new":
            msg = Message.from_dict(update.object["message"], api)
            from .fsm.context import FSMContext

            data["message"] = msg
            data["state"] = FSMContext(storage, msg.peer_id, msg.from_id)
            event_obj: Any = msg
        else:
            event_obj = update.object

        for handler in self._handlers:
            if handler.event_type != update.type:
                continue

            passed = all(
                [await _run_filter(f, event_obj, data) for f in handler.filters]
            )
            if passed:
                await _call_handler(handler.callback, data)
                return True

        for inc in self._sub_routers:
            if await inc.router.feed_update(update, api, storage):
                return True

        return False
