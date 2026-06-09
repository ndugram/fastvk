from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, get_type_hints

from .filters.builtin import _normalize_filter
from .types.callback import CallbackQuery
from .types.message import Message
from .types.update import Update
from .types.user import User

if TYPE_CHECKING:
    from .api.client import Bot
    from .fsm.context import FSMContext
    from .fsm.storage import BaseStorage


_sig_cache: dict[Callable[..., Any], list[tuple[str, Any]]] = {}


def _get_params(fn: Callable[..., Any]) -> list[tuple[str, Any]]:
    cached = _sig_cache.get(fn)
    if cached is not None:
        return cached
    try:
        hints = get_type_hints(fn)
    except Exception:
        hints = {}
    result = [(name, hints.get(name)) for name in inspect.signature(fn).parameters]
    _sig_cache[fn] = result
    return result


def _resolve_kwargs(fn: Callable[..., Any], context: dict[type, Any]) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    for name, annotation in _get_params(fn):
        if annotation is None:
            continue
        if annotation in context:
            kwargs[name] = context[annotation]
            continue
        if isinstance(annotation, type):
            for ctx_type, val in context.items():
                if isinstance(ctx_type, type) and issubclass(ctx_type, annotation):
                    kwargs[name] = val
                    break
    return kwargs


@dataclass(frozen=True, slots=True)
class _HandlerDef:
    callback: Callable[..., Any]
    filters: tuple[Callable[..., Any], ...]
    event_type: str


@dataclass(frozen=True, slots=True)
class _ErrorHandlerDef:
    callback: Callable[..., Any]
    exc_types: tuple[type[BaseException], ...]


@dataclass(slots=True)
class _IncludeDef:
    router: Router


async def _run_filter(f: Callable[..., Any], event: Any, context: dict[type, Any]) -> bool:
    result = f(event, context)
    if asyncio.iscoroutine(result):
        result = await result
    return bool(result)


class Router:
    """
    Groups related event handlers.

    ```python
    router = Router()

    @router.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer("Привет!")

    bot.include_router(router)
    ```
    """

    def __init__(self) -> None:
        self._handlers: list[_HandlerDef] = []
        self._error_handlers: list[_ErrorHandlerDef] = []
        self._sub_routers: list[_IncludeDef] = []

    def include_router(self, router: Router) -> None:
        self._sub_routers.append(_IncludeDef(router=router))

    def _register(
        self,
        event_type: str,
        *filters: Callable[..., Any],
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            normalized = tuple(_normalize_filter(f) for f in filters)
            self._handlers.append(
                _HandlerDef(callback=func, filters=normalized, event_type=event_type)
            )
            return func

        return decorator

    def message(self, *filters: Callable[..., Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Register a handler for ``message_new`` events.

        ```python
        @router.message(Command("ping"))
        async def ping(message: Message) -> None:
            await message.answer("pong")
        ```
        """
        return self._register("message_new", *filters)

    def message_reply(self, *filters: Callable[..., Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a handler for ``message_reply`` events."""
        return self._register("message_reply", *filters)

    def message_allow(self, *filters: Callable[..., Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a handler for ``message_allow`` (newsletter opt-in) events."""
        return self._register("message_allow", *filters)

    def group_join(self, *filters: Callable[..., Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a handler fired when a user joins the group."""
        return self._register("group_join", *filters)

    def group_leave(self, *filters: Callable[..., Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a handler fired when a user leaves the group."""
        return self._register("group_leave", *filters)

    def wall_post_new(self, *filters: Callable[..., Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a handler for new wall posts."""
        return self._register("wall_post_new", *filters)

    def callback(self, *filters: Callable[..., Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Register a handler for inline button presses (``message_event``).

        ```python
        @router.callback()
        async def on_click(callback: CallbackQuery) -> None:
            v = callback.payload.get("v")
            await callback.answer(f"Нажато: {v}")
        ```
        """
        return self._register("message_event", *filters)

    def exception_handler(self, *exc_types: type[BaseException]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Register an error handler for one or more exception types.

        ```python
        from fastvk.exceptions import VKAPIError

        @bot.exception_handler(VKAPIError)
        async def on_vk_error(error: VKAPIError, message: Message) -> None:
            await message.answer("VK API недоступен")

        @bot.exception_handler()
        async def on_any_error(error: Exception, message: Message) -> None:
            await message.answer(f"Ошибка: {error}")
        ```
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            types = exc_types if exc_types else (Exception,)
            self._error_handlers.append(_ErrorHandlerDef(callback=func, exc_types=types))
            return func
        return decorator

    async def _dispatch_error(self, exc: BaseException, context: dict[type, Any]) -> bool:
        err_context = {**context, type(exc): exc, Exception: exc, BaseException: exc}
        for eh in self._error_handlers:
            if isinstance(exc, eh.exc_types):
                kwargs = _resolve_kwargs(eh.callback, err_context)
                if inspect.iscoroutinefunction(eh.callback):
                    await eh.callback(**kwargs)
                else:
                    eh.callback(**kwargs)
                return True
        for inc in self._sub_routers:
            if await inc.router._dispatch_error(exc, context):
                return True
        return False

    def on(self, event_type: str, *filters: Callable[..., Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Register a handler for any VK event type by name.

        ```python
        @router.on("photo_new")
        async def new_photo(event: dict) -> None:
            print(event)
        ```
        """
        return self._register(event_type, *filters)

    async def feed_update(
        self,
        update: Update,
        bot: Bot,
        storage: BaseStorage,
    ) -> bool:
        """Dispatch *update* to the first matching handler. Returns ``True`` if handled."""
        from .api.client import Bot as _Bot
        from .fsm.context import FSMContext

        context: dict[type, Any] = {_Bot: bot, Update: update}

        if update.type == "message_new":
            msg = Message.from_dict(update.object["message"], bot)
            context[Message] = msg
            context[FSMContext] = FSMContext(storage, msg.peer_id, msg.from_id)
            event_obj: Any = msg
        elif update.type == "message_event":
            cb = CallbackQuery.from_dict(update.object, bot)
            context[CallbackQuery] = cb
            context[FSMContext] = FSMContext(storage, cb.peer_id, cb.user_id)
            event_obj = cb
        else:
            event_obj = update.object

        for handler in self._handlers:
            if handler.event_type != update.type:
                continue
            passed = all([await _run_filter(f, event_obj, context) for f in handler.filters])
            if passed:
                if update.type == "message_new" and User not in context:
                    if any(ann is User for _, ann in _get_params(handler.callback)):
                        msg = context[Message]
                        raw = await bot.users.get(user_ids=msg.from_id)
                        context[User] = User.from_dict(raw[0])
                kwargs = _resolve_kwargs(handler.callback, context)
                try:
                    if inspect.iscoroutinefunction(handler.callback):
                        await handler.callback(**kwargs)
                    else:
                        handler.callback(**kwargs)
                except Exception as exc:
                    if not await self._dispatch_error(exc, context):
                        raise
                return True

        for inc in self._sub_routers:
            if await inc.router.feed_update(update, bot, storage):
                return True

        return False
