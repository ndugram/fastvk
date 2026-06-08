from __future__ import annotations

from abc import ABC, abstractmethod

_Key = tuple[int, int]  # (peer_id, user_id)


class BaseStorage(ABC):
    """Abstract FSM storage backend."""

    @abstractmethod
    async def get_state(self, key: _Key) -> str | None:
        """Return the current state for *key*, or ``None`` if not set."""

    @abstractmethod
    async def set_state(self, key: _Key, state: str | None) -> None:
        """Set (or clear) the state for *key*."""

    @abstractmethod
    async def get_data(self, key: _Key) -> dict:
        """Return the stored data dict for *key*."""

    @abstractmethod
    async def set_data(self, key: _Key, data: dict) -> None:
        """Replace the stored data dict for *key*."""

    @abstractmethod
    async def close(self) -> None:
        """Release any resources held by the storage."""


class MemoryStorage(BaseStorage):
    """
    In-process FSM storage backed by plain Python dicts.

    Data is lost on restart. Suitable for development and single-process bots.

    ```python
    bot = FastVK(token="...", group_id=123, storage=MemoryStorage())
    ```
    """

    def __init__(self) -> None:
        self._states: dict[_Key, str] = {}
        self._data: dict[_Key, dict] = {}

    async def get_state(self, key: _Key) -> str | None:
        return self._states.get(key)

    async def set_state(self, key: _Key, state: str | None) -> None:
        if state is None:
            self._states.pop(key, None)
        else:
            self._states[key] = state

    async def get_data(self, key: _Key) -> dict:
        return dict(self._data.get(key, {}))

    async def set_data(self, key: _Key, data: dict) -> None:
        if data:
            self._data[key] = data
        else:
            self._data.pop(key, None)

    async def close(self) -> None:
        self._states.clear()
        self._data.clear()
