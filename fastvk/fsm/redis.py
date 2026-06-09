from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from .storage import BaseStorage, _Key

if TYPE_CHECKING:
    from redis.asyncio import Redis


class RedisStorage(BaseStorage):
    """
    FSM storage backed by Redis. State survives bot restarts.

    Requires ``redis`` package: ``pip install redis``.

    ```python
    from fastvk.fsm.redis import RedisStorage

    storage = RedisStorage.from_url("redis://localhost:6379/0")
    bot = FastVK(token="...", group_id=123, storage=storage)
    ```
    """

    def __init__(self, redis: Redis, *, prefix: str = "fastvk") -> None:
        self._redis = redis
        self._prefix = prefix

    @classmethod
    def from_url(cls, url: str, *, prefix: str = "fastvk", **kwargs: Any) -> RedisStorage:
        """Create storage from a Redis URL, e.g. ``"redis://localhost:6379/0"``."""
        try:
            from redis.asyncio import from_url as redis_from_url
        except ImportError as e:
            raise ImportError(
                "RedisStorage requires the 'redis' package. "
                "Install it: pip install redis"
            ) from e
        return cls(redis_from_url(url, **kwargs), prefix=prefix)

    def _state_key(self, key: _Key) -> str:
        return f"{self._prefix}:state:{key[0]}:{key[1]}"

    def _data_key(self, key: _Key) -> str:
        return f"{self._prefix}:data:{key[0]}:{key[1]}"

    async def get_state(self, key: _Key) -> str | None:
        val = await self._redis.get(self._state_key(key))
        return val.decode() if val else None

    async def set_state(self, key: _Key, state: str | None) -> None:
        if state is None:
            await self._redis.delete(self._state_key(key))
        else:
            await self._redis.set(self._state_key(key), state)

    async def get_data(self, key: _Key) -> dict:
        val = await self._redis.get(self._data_key(key))
        return json.loads(val) if val else {}

    async def set_data(self, key: _Key, data: dict) -> None:
        if data:
            await self._redis.set(
                self._data_key(key),
                json.dumps(data, ensure_ascii=False),
            )
        else:
            await self._redis.delete(self._data_key(key))

    async def close(self) -> None:
        await self._redis.aclose()
