from __future__ import annotations

from typing import Any

import aiohttp

from ..exceptions import VKAPIError

class _APIMethod:
    __slots__ = ("_client", "_prefix")

    def __init__(self, client: Bot, prefix: str) -> None:
        self._client = client
        self._prefix = prefix

    def __getattr__(self, name: str) -> _APICallable:
        return _APICallable(self._client, f"{self._prefix}.{name}")


class _APICallable:
    __slots__ = ("_client", "_method")

    def __init__(self, client: Bot, method: str) -> None:
        self._client = client
        self._method = method

    async def __call__(self, **kwargs: Any) -> Any:
        return await self._client._call(self._method, **kwargs)


class Bot:
    """
    Async VK Bot API client with dynamic method dispatch.

    ```python
    bot = Bot(token="vk1.a....")
    await bot.messages.send(peer_id=123, message="Hello", random_id=0)
    await bot.users.get(user_ids=1)
    ```
    """

    _base_url = "https://api.vk.com/method/"

    def __init__(self, token: str, version: str = "5.199") -> None:
        self.token = token
        self.version = version
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _call(self, method: str, **kwargs: Any) -> Any:
        session = await self._get_session()
        params = {"access_token": self.token, "v": self.version, **kwargs}
        async with session.post(f"{self._base_url}{method}", data=params) as resp:
            data: dict = await resp.json(content_type=None)
        if "error" in data:
            raise VKAPIError(data["error"])
        return data.get("response")

    def __getattr__(self, name: str) -> _APIMethod:
        return _APIMethod(self, name)

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()


APIClient = Bot  # backward compat alias
