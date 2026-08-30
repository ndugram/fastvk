from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, get_type_hints

from .api.client import Bot
from .background import BackgroundTasks
from .filters.builtin import _normalize_filter
from .fsm.context import FSMContext
from .fsm.storage import BaseStorage
from .types.callback import CallbackQuery
from .types.events import GroupJoinEvent, GroupLeaveEvent, WallPostEvent
from .types.message import Message
from .types.update import Update
from .types.user import User

logger = logging.getLogger("fastvk")


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


class _Context(dict):
    """Handler context dict with support for lazily-resolved providers.

    Behaves like a plain ``dict`` (filters mutate it directly), but a type
    can register an async factory that is only invoked when some handler
    actually asks for that type — avoiding e.g. an extra ``users.get`` call
    on every update.
    """

    __slots__ = ("_providers",)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._providers: dict[type, Callable[[], Awaitable[Any]]] = {}

    def provide(self, tp: type, factory: Callable[[], Awaitable[Any]]) -> None:
        self._providers[tp] = factory

    async def resolve(self, tp: Any) -> Any:
        if tp in self:
            return self[tp]
        factory = self._providers.get(tp)
        if factory is None:
            return None
        value = await factory()
        self[tp] = value
        return value


def _resolve_kwargs(fn: Callable[..., Any], context: dict[type, Any]) -> dict[str, Any]:
    """Synchronous DI resolution (no lazy providers). Kept for error handlers/tests."""
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


async def _resolve_kwargs_async(
    fn: Callable[..., Any], context: _Context
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    for name, annotation in _get_params(fn):
        if annotation is None:
            continue
        if annotation in context:
            kwargs[name] = context[annotation]
            continue
        resolved = await context.resolve(annotation)
        if resolved is not None or annotation in context:
            kwargs[name] = context.get(annotation)
            continue
        if isinstance(annotation, type):
            for ctx_type, val in list(context.items()):
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


def _log_handler(event_type: str, fn: Callable[..., Any], context: dict[type, Any]) -> None:
    parts = [f"← {event_type}", f"→ {fn.__name__}()"]
    msg = context.get(Message)
    if msg is not None:
        user = msg.from_user
        if user is not None:
            parts.append(f"[{user.full_name}  id={user.id}]")
        else:
            parts.append(f"[peer={msg.peer_id}]")
    logger.info("  ".join(parts))


async def _run_filter(f: Callable[..., Any], event: Any, context: dict[type, Any]) -> bool:
    result = f(event, context)
    if asyncio.iscoroutine(result):
        result = await result
    return bool(result)


async def _all_filters_pass(
    filters: tuple[Callable[..., Any], ...], event: Any, context: dict[type, Any]
) -> bool:
    """Evaluate filters in order, short-circuiting on the first failure."""
    for f in filters:
        if not await _run_filter(f, event, context):
            return False
    return True


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
        self._middlewares: list[Any] = []
        self._startup: list[Callable[..., Any]] = []
        self._shutdown: list[Callable[..., Any]] = []

    def include_router(self, router: Router) -> None:
        self._sub_routers.append(_IncludeDef(router=router))

    def middleware(self, mw: Any) -> Any:
        """Register a middleware that wraps handlers of this router (and sub-routers)."""
        self._middlewares.append(mw)
        return mw

    def startup(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Register a coroutine to run once when the bot starts."""
        self._startup.append(fn)
        return fn

    def shutdown(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Register a coroutine to run once when the bot stops."""
        self._shutdown.append(fn)
        return fn

    async def _emit_startup(self, context: dict[type, Any]) -> None:
        for fn in self._startup:
            await _maybe_await(fn(**_resolve_kwargs(fn, context)))
        for inc in self._sub_routers:
            await inc.router._emit_startup(context)

    async def _emit_shutdown(self, context: dict[type, Any]) -> None:
        for fn in self._shutdown:
            try:
                await _maybe_await(fn(**_resolve_kwargs(fn, context)))
            except Exception:
                logger.exception("shutdown hook %r failed", getattr(fn, "__name__", fn))
        for inc in self._sub_routers:
            await inc.router._emit_shutdown(context)

    def _collect_all_handlers(self) -> list[_HandlerDef]:
        result = list(self._handlers)
        for inc in self._sub_routers:
            result.extend(inc.router._collect_all_handlers())
        return result

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

    def message_edit(self, *filters: Callable[..., Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a handler for ``message_edit`` events."""
        return self._register("message_edit", *filters)

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

    def _build_context(self, update: Update, bot: Bot, storage: BaseStorage) -> _Context:
        context: _Context = _Context({Bot: bot, Update: update})

        async def _fetch_user(uid: int) -> User | None:
            try:
                raw = await bot.users.get(user_ids=uid)
                return User.from_dict(raw[0])
            except Exception:
                return None

        if update.type in ("message_new", "message_reply", "message_edit"):
            raw_msg = update.object.get("message", update.object)
            msg = Message.from_dict(raw_msg, bot)
            context[Message] = msg
            context[FSMContext] = FSMContext(storage, msg.peer_id, msg.from_id)

            async def _user_for_msg() -> User | None:
                user = await _fetch_user(msg.from_id)
                if user is not None:
                    msg._from_user = user
                return user

            context.provide(User, _user_for_msg)
        elif update.type == "message_event":
            cb = CallbackQuery.from_dict(update.object, bot)
            context[CallbackQuery] = cb
            context[FSMContext] = FSMContext(storage, cb.peer_id, cb.user_id)

            async def _user_for_cb() -> User | None:
                user = await _fetch_user(cb.user_id)
                if user is not None:
                    cb._from_user = user
                return user

            context.provide(User, _user_for_cb)
        elif update.type == "group_join":
            evt = GroupJoinEvent.from_dict(update.object)
            context[GroupJoinEvent] = evt
            context.provide(User, lambda: _fetch_user(evt.user_id))
        elif update.type == "group_leave":
            evt2 = GroupLeaveEvent.from_dict(update.object)
            context[GroupLeaveEvent] = evt2
            context.provide(User, lambda: _fetch_user(evt2.user_id))
        elif update.type == "wall_post_new":
            evt3 = WallPostEvent.from_dict(update.object)
            context[WallPostEvent] = evt3
            if evt3.from_id > 0:
                context.provide(User, lambda: _fetch_user(evt3.from_id))
        return context

    @staticmethod
    def _event_obj(update: Update, context: _Context) -> Any:
        for tp in (Message, CallbackQuery, GroupJoinEvent, GroupLeaveEvent, WallPostEvent):
            if tp in context:
                return context[tp]
        return update.object

    async def feed_update(
        self,
        update: Update,
        bot: Bot,
        storage: BaseStorage,
        data: dict[Any, Any] | None = None,
    ) -> bool:
        """Dispatch *update* to the first matching handler. Returns ``True`` if handled."""
        context = self._build_context(update, bot, storage)
        _merge_data(context, data)
        return await self._feed(update, bot, storage, context)

    async def _feed(
        self,
        update: Update,
        bot: Bot,
        storage: BaseStorage,
        context: _Context,
    ) -> bool:
        event_obj = self._event_obj(update, context)

        async def _dispatch() -> bool:
            for handler in self._handlers:
                if handler.event_type != update.type:
                    continue
                if not await _all_filters_pass(handler.filters, event_obj, context):
                    continue
                bg = BackgroundTasks()
                context[BackgroundTasks] = bg
                kwargs = await _resolve_kwargs_async(handler.callback, context)
                _log_handler(update.type, handler.callback, context)
                try:
                    if inspect.iscoroutinefunction(handler.callback):
                        await handler.callback(**kwargs)
                    else:
                        handler.callback(**kwargs)
                except Exception as exc:
                    logger.exception(
                        "← %s  [%s]  unhandled exception",
                        update.type, handler.callback.__name__,
                    )
                    if not await self._dispatch_error(exc, context):
                        raise
                if bg._tasks:
                    asyncio.create_task(bg._run())
                return True

            for inc in self._sub_routers:
                if await inc.router._feed(update, bot, storage, context):
                    return True
            return False

        if not self._middlewares:
            return await _dispatch()

        async def _root(_e: Any, _d: dict) -> Any:
            return await _dispatch()

        chain: Callable[[Any, dict], Awaitable[Any]] = _root
        for mw in reversed(self._middlewares):
            chain = _wrap_mw(mw, chain)
        return bool(await chain(event_obj, context))


def _wrap_mw(
    mw: Any, nxt: Callable[[Any, dict], Awaitable[Any]]
) -> Callable[[Any, dict], Awaitable[Any]]:
    async def _call(event: Any, data: dict) -> Any:
        return await mw(nxt, event, data)

    return _call


def _merge_data(context: _Context, data: dict[Any, Any] | None) -> None:
    if not data:
        return
    for key, value in data.items():
        if isinstance(key, type):
            context.setdefault(key, value)
        else:
            context.setdefault(type(value), value)
        context.setdefault(key, value)


async def _maybe_await(result: Any) -> Any:
    if inspect.isawaitable(result):
        return await result
    return result
