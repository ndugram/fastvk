from __future__ import annotations

from typing import Any


def _resolve(event: Any, path: tuple[str, ...]) -> Any:
    obj = event
    for attr in path:
        if obj is None:
            return None
        obj = obj.get(attr) if isinstance(obj, dict) else getattr(obj, attr, None)
    return obj


class _BaseFilter:
    def __call__(self, event: Any, context: dict) -> bool:  # noqa: ARG002
        raise NotImplementedError

    def __and__(self, other: _BaseFilter) -> _AndFilter:
        return _AndFilter(self, other)

    def __or__(self, other: _BaseFilter) -> _OrFilter:
        return _OrFilter(self, other)

    def __invert__(self) -> _NotFilter:
        return _NotFilter(self)


class _OpFilter(_BaseFilter):
    __slots__ = ("_path", "_op", "_value")

    def __init__(self, path: tuple[str, ...], op: str, value: Any) -> None:
        self._path = path
        self._op = op
        self._value = value

    def __call__(self, event: Any, context: dict) -> bool:  # noqa: ARG002
        v = _resolve(event, self._path)
        if self._op == "==":
            return bool(v == self._value)
        if self._op == "!=":
            return bool(v != self._value)
        if self._op == "in":
            return v in self._value
        if self._op == "not_in":
            return v not in self._value
        if self._op == "startswith":
            return isinstance(v, str) and v.startswith(self._value)
        if self._op == "endswith":
            return isinstance(v, str) and v.endswith(self._value)
        if self._op == "contains":
            return v is not None and self._value in v
        if self._op == "regexp":
            import re
            return isinstance(v, str) and bool(re.search(self._value, v))
        return False


class _AndFilter(_BaseFilter):
    __slots__ = ("_a", "_b")

    def __init__(self, a: _BaseFilter, b: _BaseFilter) -> None:
        self._a, self._b = a, b

    def __call__(self, event: Any, context: dict) -> bool:
        return self._a(event, context) and self._b(event, context)


class _OrFilter(_BaseFilter):
    __slots__ = ("_a", "_b")

    def __init__(self, a: _BaseFilter, b: _BaseFilter) -> None:
        self._a, self._b = a, b

    def __call__(self, event: Any, context: dict) -> bool:
        return self._a(event, context) or self._b(event, context)


class _NotFilter(_BaseFilter):
    __slots__ = ("_f",)

    def __init__(self, f: _BaseFilter) -> None:
        self._f = f

    def __call__(self, event: Any, context: dict) -> bool:
        return not self._f(event, context)


class MagicFilter(_BaseFilter):
    """Lazy expression filter. Use the root object ``F`` to build filter expressions.

    ```python
    from fastvk import F

    @bot.message(F.text == "привет")
    async def on_hi(message: Message) -> None:
        await message.answer("Привет!")

    @bot.message(F.text.startswith("/"))
    async def on_command(message: Message) -> None: ...

    @bot.message(F.text.contains("скидка") | F.text.contains("акция"))
    async def on_promo(message: Message) -> None: ...

    @bot.message(~F.text.startswith("/"))
    async def not_command(message: Message) -> None: ...

    @bot.callback(F.payload == {"action": "buy"})
    async def on_buy(callback: CallbackQuery) -> None: ...

    @bot.callback(F.payload.action == "buy")
    async def on_buy2(callback: CallbackQuery) -> None: ...
    ```
    """

    __slots__ = ("_path",)

    def __init__(self, path: tuple[str, ...] = ()) -> None:
        self._path = path

    def __getattr__(self, name: str) -> MagicFilter:
        return MagicFilter(self._path + (name,))

    def __eq__(self, other: object) -> _OpFilter:  # type: ignore[override]
        return _OpFilter(self._path, "==", other)

    def __ne__(self, other: object) -> _OpFilter:  # type: ignore[override]
        return _OpFilter(self._path, "!=", other)

    __hash__ = None  # type: ignore[assignment]

    def in_(self, *values: Any) -> _OpFilter:
        """Match if the field value equals one of *values*."""
        return _OpFilter(self._path, "in", values)

    def not_in_(self, *values: Any) -> _OpFilter:
        """Match if the field value is not in *values*."""
        return _OpFilter(self._path, "not_in", values)

    def startswith(self, prefix: str) -> _OpFilter:
        """Match if the string field starts with *prefix*."""
        return _OpFilter(self._path, "startswith", prefix)

    def endswith(self, suffix: str) -> _OpFilter:
        """Match if the string field ends with *suffix*."""
        return _OpFilter(self._path, "endswith", suffix)

    def contains(self, substr: str) -> _OpFilter:
        """Match if *substr* is found in the field value."""
        return _OpFilter(self._path, "contains", substr)

    def regexp(self, pattern: str) -> _OpFilter:
        """Match if the string field matches the regular expression."""
        return _OpFilter(self._path, "regexp", pattern)

    def __call__(self, event: Any, context: dict) -> bool:  # noqa: ARG002
        return bool(_resolve(event, self._path))


F = MagicFilter()
