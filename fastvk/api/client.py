from __future__ import annotations

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable
from pathlib import Path
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

# 1  — unknown error (try again)
# 6  — too many requests per second
# 9  — flood control
# 10 — internal server error
# 29 — rate limit reached
_RETRYABLE_CODES = frozenset({1, 6, 9, 10, 29})

_CAPTCHA_CODE = 14

DEFAULT_TIMEOUT = 30.0

# Signature of a captcha solver: receives the captcha image URL, returns the answer.
CaptchaHandler = Callable[[str, str], Awaitable[str]]


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
        timeout: float = DEFAULT_TIMEOUT,
        captcha_handler: CaptchaHandler | None = None,
    ) -> None:
        self.token = token
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._captcha_handler = captcha_handler
        self._session: aiohttp.ClientSession | None = None

    def set_captcha_handler(self, handler: CaptchaHandler) -> None:
        """Register a coroutine that solves captchas: ``(sid, img_url) -> answer``."""
        self._captcha_handler = handler

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self._session

    async def _call(self, method: str, **kwargs: Any) -> Any:
        captcha_sid: str | None = None
        captcha_key: str | None = None

        for attempt in range(self._max_retries + 1):
            try:
                session = await self._get_session()
                params = {"access_token": self.token, "v": self._version, **kwargs}
                params = {k: v for k, v in params.items() if v is not None}
                if captcha_sid is not None and captcha_key is not None:
                    params["captcha_sid"] = captcha_sid
                    params["captcha_key"] = captcha_key
                async with session.post(
                    f"{self._base_url}{method}", data=params
                ) as resp:
                    data: dict = await resp.json(content_type=None)
                if "error" in data:
                    err = data["error"]
                    code = err.get("error_code", 0)

                    solver = self._captcha_handler
                    if code == _CAPTCHA_CODE and solver is not None:
                        sid = str(err.get("captcha_sid", ""))
                        img = str(err.get("captcha_img", ""))
                        logger.warning("VK captcha required on %s (sid=%s)", method, sid)
                        try:
                            answer = await solver(sid, img)
                        except Exception:
                            logger.exception("Captcha handler raised")
                            raise VKAPIError(err) from None
                        captcha_sid, captcha_key = sid, answer
                        continue

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
                    raise VKAPIError(err)
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

    async def execute(self, code: str) -> Any:
        """
        Run a VKScript snippet server-side via ``execute`` (up to 25 API calls at once).

        ```python
        result = await bot.execute('''
            var a = API.users.get({"user_ids": 1});
            var b = API.users.get({"user_ids": 2});
            return [a, b];
        ''')
        ```
        """
        return await self._call("execute", code=code)

    async def execute_batch(
        self,
        calls: list[tuple[str, dict[str, Any]]],
    ) -> list[Any]:
        """
        Run up to 25 API calls in a single request and return their results in order.

        ```python
        results = await bot.execute_batch([
            ("users.get", {"user_ids": 1}),
            ("groups.getById", {"group_id": 1}),
        ])
        ```
        """
        import json as _json

        if len(calls) > 25:
            raise ValueError("execute_batch accepts at most 25 calls per request")
        parts = [
            f'API.{method}({_json.dumps(args, ensure_ascii=False)})'
            for method, args in calls
        ]
        code = "return [" + ",".join(parts) + "];"
        result = await self.execute(code)
        return result if isinstance(result, list) else []

    async def download(
        self,
        url: str,
        dest: str | Path | None = None,
    ) -> bytes:
        """
        Download a file (e.g. an attachment URL) and return its bytes.

        If *dest* is given, the content is also written to that path.
        """
        session = await self._get_session()
        async with session.get(url) as resp:
            resp.raise_for_status()
            content = await resp.read()
        if dest is not None:
            Path(dest).write_bytes(content)
        return content

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
        total = 0

        while True:
            inst = method_class(count=count, offset=offset, **kwargs)  # type: ignore[call-arg]
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
