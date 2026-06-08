from __future__ import annotations


class FastVKError(Exception):
    """Base exception for all FastVK errors."""


class VKAPIError(FastVKError):
    """Raised when VK API returns an error response."""

    def __init__(self, error_data: dict) -> None:
        self.code: int = error_data.get("error_code", 0)
        self.message: str = error_data.get("error_msg", "Unknown error")
        self.request_params: list = error_data.get("request_params", [])
        super().__init__(f"[{self.code}] {self.message}")


class HandlerNotFoundError(FastVKError):
    """Raised when no handler matched the incoming update."""


class FilterError(FastVKError):
    """Raised when a filter fails unexpectedly."""


class StorageError(FastVKError):
    """Raised on FSM storage failures."""


class PollingError(FastVKError):
    """Raised on Long Poll failures that cannot be recovered."""
