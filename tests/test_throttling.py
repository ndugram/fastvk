from __future__ import annotations

import time
from typing import Any
from unittest.mock import AsyncMock

import pytest

from fastvk.middleware.throttling import ThrottlingMiddleware
from fastvk.types.update import Update


def _update(user_id: int, event_type: str = "message_new") -> Update:
    if event_type == "message_new":
        obj: dict[str, Any] = {"message": {"from_id": user_id, "text": "hi"}}
    else:
        obj = {"user_id": user_id}
    return Update(type=event_type, object=obj, group_id=1, event_id="x")


class TestThrottlingMiddleware:
    async def test_first_call_passes(self) -> None:
        mw = ThrottlingMiddleware(rate=1.0)
        handler = AsyncMock(return_value="ok")
        result = await mw(handler, _update(1), {})
        assert result == "ok"
        handler.assert_awaited_once()

    async def test_second_call_within_rate_is_dropped(self) -> None:
        mw = ThrottlingMiddleware(rate=1.0)
        handler = AsyncMock(return_value="ok")
        await mw(handler, _update(1), {})
        result = await mw(handler, _update(1), {})
        assert result is None
        assert handler.await_count == 1

    async def test_second_call_after_rate_passes(self) -> None:
        mw = ThrottlingMiddleware(rate=0.05)
        handler = AsyncMock(return_value="ok")
        await mw(handler, _update(1), {})
        time.sleep(0.06)
        result = await mw(handler, _update(1), {})
        assert result == "ok"
        assert handler.await_count == 2

    async def test_different_users_independent(self) -> None:
        mw = ThrottlingMiddleware(rate=1.0)
        handler = AsyncMock(return_value="ok")
        await mw(handler, _update(1), {})
        result = await mw(handler, _update(2), {})
        assert result == "ok"
        assert handler.await_count == 2

    async def test_same_user_throttled_after_burst(self) -> None:
        mw = ThrottlingMiddleware(rate=1.0)
        handler = AsyncMock(return_value="ok")
        for _ in range(5):
            await mw(handler, _update(42), {})
        assert handler.await_count == 1

    async def test_group_join_event_user_id(self) -> None:
        mw = ThrottlingMiddleware(rate=1.0)
        handler = AsyncMock(return_value="ok")
        update = _update(99, event_type="group_join")
        await mw(handler, update, {})
        result = await mw(handler, update, {})
        assert result is None
        assert handler.await_count == 1

    async def test_non_update_object_passes_through(self) -> None:
        mw = ThrottlingMiddleware(rate=1.0)
        handler = AsyncMock(return_value="ok")
        result = await mw(handler, "not_an_update", {})
        assert result == "ok"

    async def test_rate_zero_disabled(self) -> None:
        """rate=0 should never be registered — but ThrottlingMiddleware itself still works."""
        mw = ThrottlingMiddleware(rate=0.0)
        handler = AsyncMock(return_value="ok")
        r1 = await mw(handler, _update(1), {})
        r2 = await mw(handler, _update(1), {})
        assert r1 == "ok"
        assert r2 == "ok"

    async def test_negative_from_id_passes_through(self) -> None:
        mw = ThrottlingMiddleware(rate=1.0)
        handler = AsyncMock(return_value="ok")
        update = Update(
            type="wall_post_new",
            object={"from_id": -100500, "id": 1, "owner_id": -100500, "date": 0, "text": ""},
            group_id=1,
            event_id="x",
        )
        r1 = await mw(handler, update, {})
        r2 = await mw(handler, update, {})
        assert r1 == "ok"
        assert r2 == "ok"
