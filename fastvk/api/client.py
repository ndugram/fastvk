from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import aiohttp

from ..__meta__ import _api_base_url_, _api_version_
from ..exceptions import VKAPIError
from ..types.group import Group

if TYPE_CHECKING:
    from ..methods.base import VKMethod

_T = TypeVar("_T")


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
        from ..methods import _REGISTRY
        method_cls = _REGISTRY.get(self._method)
        if method_cls is not None:
            return await self._client(method_cls(**kwargs))
        return await self._client._call(self._method, **kwargs)


class Bot:
    """
    Async VK Bot API client with dynamic method dispatch.

    Supports both dynamic calls and typed :class:`~fastvk.methods.VKMethod` objects:

    ```python
    bot = Bot(token="vk1.a....")

    # dynamic (any VK method)
    await bot.messages.send(peer_id=123, message="Hello", random_id=0)

    # typed (IDE autocomplete + validation)
    from fastvk.methods import MessagesSend
    await bot(MessagesSend(peer_id=123, message="Hello"))
    ```
    """

    _base_url = _api_base_url_
    _version = _api_version_

    def __init__(self, token: str) -> None:
        self.token = token
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _call(self, method: str, **kwargs: Any) -> Any:
        session = await self._get_session()
        params = {"access_token": self.token, "v": self._version, **kwargs}
        async with session.post(f"{self._base_url}{method}", data=params) as resp:
            data: dict = await resp.json(content_type=None)
        if "error" in data:
            raise VKAPIError(data["error"])
        return data.get("response")

    async def __call__(self, method: VKMethod[_T]) -> _T:
        params = method.model_dump(exclude_none=True)
        return await self._call(method.__api_method__, **params)

    async def get_me(self) -> Group:
        """Return info about the community this token belongs to."""
        data = await self._call(
            "groups.getById",
            fields="description,members_count,screen_name",
        )
        return Group.from_dict(data[0])

    def __getattr__(self, name: str) -> _APIMethod:
        return _APIMethod(self, name)

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()


APIClient = Bot  # backward compat alias
