from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from .base import BaseMiddleware

logger = logging.getLogger("fastvk.i18n")

_current_locale: ContextVar[str] = ContextVar("fastvk_locale", default="en")


class I18n:
    """
    Tiny JSON-catalog translator.

    Expects a directory of ``<locale>.json`` files, each a flat ``{key: text}`` map:

    ```
    locales/
      en.json   {"hello": "Hello, {name}!"}
      ru.json   {"hello": "Привет, {name}!"}
    ```

    ```python
    i18n = I18n("locales", default_locale="ru")
    bot = FastVK(token="...", middleware=[I18nMiddleware(i18n)])

    @bot.message()
    async def h(message: Message, i18n: I18n) -> None:
        await message.answer(i18n("hello", name=message.from_id))
    ```
    """

    def __init__(self, path: str | Path, *, default_locale: str = "en") -> None:
        self.path = Path(path)
        self.default_locale = default_locale
        self.catalogs: dict[str, dict[str, str]] = {}
        self.reload()

    def reload(self) -> None:
        self.catalogs.clear()
        if not self.path.is_dir():
            logger.warning("i18n path %s does not exist", self.path)
            return
        for file in self.path.glob("*.json"):
            try:
                self.catalogs[file.stem] = json.loads(file.read_text("utf-8"))
            except Exception:
                logger.exception("failed to load locale %s", file)

    @property
    def available_locales(self) -> list[str]:
        return sorted(self.catalogs)

    def gettext(self, key: str, /, locale: str | None = None, **kwargs: Any) -> str:
        loc = locale or _current_locale.get()
        catalog = self.catalogs.get(loc) or self.catalogs.get(self.default_locale) or {}
        template = catalog.get(key, key)
        try:
            return template.format(**kwargs) if kwargs else template
        except (KeyError, IndexError):
            return template

    __call__ = gettext

    @staticmethod
    def set_locale(locale: str) -> None:
        _current_locale.set(locale)

    @staticmethod
    def get_locale() -> str:
        return _current_locale.get()


class I18nMiddleware(BaseMiddleware):
    """
    Resolves the locale for each update and exposes the translator to handlers.

    Injects ``I18n`` and ``I18n.Gettext`` (a callable bound to the resolved
    locale) into the DI context.
    """

    def __init__(
        self,
        i18n: I18n,
        *,
        locale_getter: Callable[[Any], Awaitable[str | None]] | None = None,
    ) -> None:
        self.i18n = i18n
        self._locale_getter = locale_getter

    async def _resolve_locale(self, event: Any) -> str:
        if self._locale_getter is not None:
            got = await self._locale_getter(event)
            if got:
                return got
        obj = getattr(event, "object", {})
        if isinstance(obj, dict):
            lang = (
                obj.get("client_info", {}).get("lang_id")
                or obj.get("message", {}).get("lang")
            )
            if isinstance(lang, str):
                return lang
        return self.i18n.default_locale

    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        locale = await self._resolve_locale(event)
        token = _current_locale.set(locale)
        try:
            # Handlers declare ``i18n: I18n`` and call ``i18n("key", ...)`` —
            # the active locale is read from the context var set above.
            data[I18n] = self.i18n
            data["locale"] = locale
            return await handler(event, data)
        finally:
            _current_locale.reset(token)


__all__ = ["I18n", "I18nMiddleware"]
