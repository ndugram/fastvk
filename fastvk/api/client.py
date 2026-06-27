from __future__ import annotations

import asyncio
import logging
import random
from typing import TYPE_CHECKING, Any, TypeVar

import aiohttp

from ..__meta__ import _api_base_url_, _api_version_
from ..exceptions import VKAPIError
from ..types.group import Group
from ..types.user import User

if TYPE_CHECKING:
    from ..methods.base import VKMethod

_M = TypeVar("_M", bound="VKMethod")
_T = TypeVar("_T")

_ITEM_KEYS = (
    "items",
    "profiles",
    "groups",
    "users",
    "posts",
    "photos",
    "videos",
    "audios",
    "topics",
    "comments",
    "messages",
)

logger = logging.getLogger("fastvk.api")

_RETRYABLE_CODES = frozenset({1, 9, 10})


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

    def __init__(
        self,
        token: str,
        *,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.token = token
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _call(self, method: str, **kwargs: Any) -> Any:
        for attempt in range(self._max_retries + 1):
            try:
                session = await self._get_session()
                params = {"access_token": self.token, "v": self._version, **kwargs}
                async with session.post(
                    f"{self._base_url}{method}", data=params
                ) as resp:
                    data: dict = await resp.json(content_type=None)
                if "error" in data:
                    code = data["error"].get("error_code", 0)
                    if attempt < self._max_retries and code in _RETRYABLE_CODES:
                        delay = self._retry_delay * (2**attempt) + random.uniform(0, 1)
                        logger.warning(
                            "VK API error %d on %s, retrying in %.1fs (attempt %d/%d)",
                            code,
                            method,
                            delay,
                            attempt + 1,
                            self._max_retries,
                        )
                        await asyncio.sleep(delay)
                        continue
                    raise VKAPIError(data["error"])
                return data.get("response")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < self._max_retries:
                    delay = self._retry_delay * (2**attempt) + random.uniform(0, 1)
                    logger.warning(
                        "Network error on %s: %s, retrying in %.1fs (attempt %d/%d)",
                        method,
                        e,
                        delay,
                        attempt + 1,
                        self._max_retries,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise
        raise RuntimeError("Unreachable")

    async def __call__(self, method: VKMethod[_T]) -> _T:
        params = method.model_dump(exclude_none=True)
        return await self._call(method.__api_method__, **params)

    async def get_user(self, user_id: int, fields: str = "") -> User:
        """Return info about a user by ID."""
        params: dict[str, Any] = {"user_ids": user_id}
        if fields:
            params["fields"] = fields
        data = await self._call("users.get", **params)
        return User.from_dict(data[0])

    async def get_me(self) -> Group:
        """Return info about the community this token belongs to."""
        data = await self._call(
            "groups.getById",
            fields="description,members_count,screen_name",
        )
        groups = data.get("groups", data) if isinstance(data, dict) else data
        return Group.from_dict(groups[0])

    def __getattr__(self, name: str) -> _APIMethod:
        return _APIMethod(self, name)

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def collect(
        self,
        method_class: type[_M],
        *,
        max_total: int = 0,
        items_key: str | None = None,
        count: int = 100,
        offset: int = 0,
        **kwargs: Any,
    ) -> list[Any]:
        """
        Collect all items from a paginated VK API method.

        Accepts a typed method class (not a string) — full IDE autocomplete.

        ```python
        from fastvk.methods import GroupsGetMembers, WallGet, MessagesGetHistory

        members = await bot.collect(GroupsGetMembers, group_id=123, fields="photo_200")
        posts   = await bot.collect(WallGet, owner_id=-123, count=50)
        history = await bot.collect(MessagesGetHistory, peer_id=2000000001)
        ```
        """
        all_items: list[Any] = []

        while True:
            inst = method_class(count=count, offset=offset, **kwargs)  # type: ignore[call-overload]
            resp = await self(inst)

            if isinstance(resp, list):
                chunk = resp
            elif isinstance(resp, dict):
                if items_key:
                    chunk = resp[items_key]
                else:
                    for key in _ITEM_KEYS:
                        if key in resp:
                            chunk = resp[key]
                            break
                    else:
                        raise KeyError(
                            f"Cannot find items in response. "
                            f"Pass `items_key=` explicitly. "
                            f"Available keys: {list(resp.keys())}"
                        )
                total = resp.get("count", 0) or resp.get("total", 0)
            else:
                break

            if not chunk:
                break

            all_items.extend(chunk)

            if max_total and len(all_items) >= max_total:
                return all_items[:max_total]

            if len(chunk) < count:
                break

            if total and offset + count >= total:
                break

            offset += count

        return all_items


APIClient = Bot  # backward compat alias
