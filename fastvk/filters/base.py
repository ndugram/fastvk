from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseFilter(ABC):
    """
    Abstract base class for all FastVK filters.

    A filter is a callable that receives an event object and a handler
    data dict, and returns a bool indicating whether the handler should run.

    Sync and async filters are both supported:

    ```python
    class MyFilter(BaseFilter):
        async def __call__(self, message: Message, data: dict) -> bool:
            return message.from_id == 123456
    ```
    """

    @abstractmethod
    async def __call__(self, event: Any, data: dict) -> bool: ...
