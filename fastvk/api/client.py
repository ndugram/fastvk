from __future__ import annotations

from typing import Any, TYPE_CHECKING

import aiohttp

from ..exceptions import VKAPIError

if TYPE_CHECKING:
    pass

VK_API_BASE = "https://api.vk.com/method/"


class _APIMethod:
    """Lazy proxy for a VK API namespace (e.g. ``messages``, ``groups``)."""

    __slots__ = ("_client", "_prefix")

    def __init__(self, client: APIClient, prefix: str) -> None:
        self._client = client
        self._prefix = prefix

    def __getattr__(self, name: str) -> _APICallable:
        return _APICallable(self._client, f"{self._prefix}.{name}")


class _APICallable:
    """Callable proxy for a single VK API method (e.g. ``messages.send``)."""

    __slots__ = ("_client", "_method")

    def __init__(self, client: APIClient, method: str) -> None:
        self._client = client
        self._method = method

    async def __call__(self, **kwargs: Any) -> Any:
        return await self._client._call(self._method, **kwargs)


class APIClient:
    """
    Async VK API client with dynamic method dispatch.

    Supports any VK API method via attribute access:

    ```python
    api = APIClient(token="...")
    await api.messages.send(peer_id=123, message="Hello", random_id=0)
    await api.users.get(user_ids=1)
    ```
    """

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
        async with session.post(f"{VK_API_BASE}{method}", data=params) as resp:
            data: dict = await resp.json(content_type=None)
        if "error" in data:
            raise VKAPIError(data["error"])
        return data.get("response")

    def __getattr__(self, name: str) -> _APIMethod:
        return _APIMethod(self, name)

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
