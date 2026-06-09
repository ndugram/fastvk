from __future__ import annotations


class FastVKError(Exception):
    """Base exception for all FastVK errors."""

    def __str__(self) -> str:
        return self.args[0] if self.args else self.__class__.__name__

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self!s})"


class VKAPIError(FastVKError):
    """Raised when VK API returns an error response."""

    def __init__(self, error_data: dict) -> None:
        self.code: int = error_data.get("error_code", 0)
        self.message: str = error_data.get("error_msg", "Unknown error")
        self.request_params: list = error_data.get("request_params", [])
        super().__init__(f"[{self.code}] {self.message}")

    def __repr__(self) -> str:
        return f"VKAPIError(code={self.code}, message={self.message!r})"


class HandlerNotFoundError(FastVKError):
    """Raised when no handler matched the incoming update."""

    def __init__(self, event_type: str) -> None:
        self.event_type = event_type
        super().__init__(f"No handler registered for event type: {event_type!r}")


class FilterError(FastVKError):
    """Raised when a filter fails unexpectedly."""

    def __init__(self, filter_name: str, cause: BaseException | None = None) -> None:
        self.filter_name = filter_name
        self.cause = cause
        msg = f"Filter {filter_name!r} raised an exception"
        if cause:
            msg += f": {cause}"
        super().__init__(msg)

    def __repr__(self) -> str:
        return f"FilterError(filter={self.filter_name!r}, cause={self.cause!r})"


class StorageError(FastVKError):
    """Raised on FSM storage failures."""

    def __init__(self, operation: str, key: str | None = None, cause: BaseException | None = None) -> None:
        self.operation = operation
        self.key = key
        self.cause = cause
        msg = f"Storage error during {operation!r}"
        if key:
            msg += f" (key={key!r})"
        if cause:
            msg += f": {cause}"
        super().__init__(msg)

    def __repr__(self) -> str:
        return f"StorageError(operation={self.operation!r}, key={self.key!r})"


class PollingError(FastVKError):
    """Raised on Long Poll failures that cannot be recovered."""

    def __init__(self, failed: int, ts: int | None = None) -> None:
        self.failed = failed
        self.ts = ts
        reasons = {
            1: "event history outdated",
            2: "server key expired",
            3: "server info lost",
        }
        reason = reasons.get(failed, "unknown failure")
        msg = f"Long Poll failed={failed} ({reason})"
        if ts is not None:
            msg += f", ts={ts}"
        super().__init__(msg)

    def __repr__(self) -> str:
        return f"PollingError(failed={self.failed}, ts={self.ts})"
