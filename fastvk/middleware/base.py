from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any


class BaseMiddleware(ABC):
    """
    Abstract base for FastVK middleware.

    Middleware wraps every handler call, allowing you to run code
    before and after each event is processed.

    ```python
    class LoggingMiddleware(BaseMiddleware):
        async def __call__(
            self,
            handler: Callable[[Any, dict], Awaitable[Any]],
            event: Any,
            data: dict,
        ) -> Any:
            print(f"Incoming: {event}")
            result = await handler(event, data)
            print(f"Handled")
            return result
    ```
    """

    @abstractmethod
    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any: ...


class MiddlewareManager:
    """
    Builds and executes a chain of middleware around a handler call.

    ```python
    manager = MiddlewareManager([LoggingMiddleware(), RateLimitMiddleware()])
    await manager.trigger(handler, event, data)
    ```
    """

    def __init__(self, middlewares: list[BaseMiddleware] | None = None) -> None:
        self._middlewares: list[BaseMiddleware] = middlewares or []

    def register(self, middleware: BaseMiddleware) -> None:
        """Append *middleware* to the chain."""
        self._middlewares.append(middleware)

    async def trigger(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        """Wrap *handler* in the full middleware chain and call it."""

        async def _build(
            idx: int,
            evt: Any,
            d: dict,
        ) -> Any:
            if idx >= len(self._middlewares):
                return await handler(evt, d)
            mw = self._middlewares[idx]
            return await mw(lambda e, dd: _build(idx + 1, e, dd), evt, d)

        return await _build(0, event, data)
