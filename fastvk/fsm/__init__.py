from __future__ import annotations

from .context import FSMContext
from .state import State, StatesGroup
from .storage import BaseStorage, MemoryStorage

__all__ = ["BaseStorage", "FSMContext", "MemoryStorage", "RedisStorage", "SQLiteStorage", "State", "StatesGroup"]


def __getattr__(name: str) -> object:
    if name == "RedisStorage":
        from .redis import RedisStorage
        return RedisStorage
    if name == "SQLiteStorage":
        from .sqlite import SQLiteStorage
        return SQLiteStorage
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
