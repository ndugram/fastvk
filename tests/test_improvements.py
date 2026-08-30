from __future__ import annotations

import asyncio
import re
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from fastvk.api.client import Bot, _RETRYABLE_CODES
from fastvk.exceptions import VKAPIError
from fastvk.filters.builtin import Command, ContentType, HasAttachment, Regexp
from fastvk.fsm.storage import MemoryStorage
from fastvk.keyboard import Button, Carousel
from fastvk.metrics import render_prometheus
from fastvk.middleware.base import BaseMiddleware
from fastvk.router import Router
from fastvk.scheduler import Scheduler, _parse_interval
from fastvk.test import MockedBot, callback_update, dispatch, message_update
from fastvk.types.attachments import Photo, parse_attachment
from fastvk.types.message import Message
from fastvk.types.user import User


# --------------------------------------------------------------------------
# 1. Correctness / performance
# --------------------------------------------------------------------------


class TestLazyUser:
    async def test_no_users_get_without_injection(
        self, mock_bot: MagicMock, storage: MemoryStorage
    ) -> None:
        router = Router()

        @router.message()
        async def h(message: Message) -> None: ...

        await dispatch(router, mock_bot, message_update("hi"), storage=storage)
        mock_bot.users.get.assert_not_called()

    async def test_users_get_once_when_injected(
        self, mock_bot: MagicMock, storage: MemoryStorage
    ) -> None:
        router = Router()
        seen: list[User] = []

        @router.message()
        async def h(message: Message, user: User) -> None:
            seen.append(user)

        await dispatch(router, mock_bot, message_update("hi"), storage=storage)
        mock_bot.users.get.assert_called_once()
        assert seen[0].id == 123456


class TestShortCircuitFilters:
    async def test_second_filter_not_run_after_first_fails(
        self, mock_bot: MagicMock, storage: MemoryStorage
    ) -> None:
        router = Router()
        calls: list[str] = []

        def f_false(event: Any, data: dict) -> bool:
            calls.append("first")
            return False

        def f_side_effect(event: Any, data: dict) -> bool:
            calls.append("second")
            return True

        @router.message(f_false, f_side_effect)
        async def h(message: Message) -> None: ...

        handled = await dispatch(
            router, mock_bot, message_update("x"), storage=storage
        )
        assert handled is False
        assert calls == ["first"]


class TestMiddlewareData:
    async def test_middleware_injects_value_by_type(
        self, mock_bot: MagicMock, storage: MemoryStorage
    ) -> None:
        class Marker:
            pass

        marker = Marker()

        class MW(BaseMiddleware):
            async def __call__(self, handler: Any, event: Any, data: dict) -> Any:
                data[Marker] = marker
                return await handler(event, data)

        root = Router()
        root.middleware(MW())
        got: list[Marker] = []

        @root.message()
        async def h(message: Message, obj: Marker) -> None:
            got.append(obj)

        await dispatch(root, mock_bot, message_update("hi"), storage=storage)
        assert got == [marker]


class TestRetryAndCaptcha:
    def test_retryable_codes_extended(self) -> None:
        assert {1, 6, 9, 10, 29} <= _RETRYABLE_CODES

    async def test_captcha_handler_invoked_and_retried(self) -> None:
        bot = Bot(token="t", max_retries=2, retry_delay=0)
        solved: list[str] = []

        async def solver(sid: str, img: str) -> str:
            solved.append(sid)
            return "answer"

        bot.set_captcha_handler(solver)

        responses = [
            {"error": {"error_code": 14, "captcha_sid": "S1", "captcha_img": "u"}},
            {"response": {"ok": 1}},
        ]

        class _Resp:
            def __init__(self, payload: dict) -> None:
                self._payload = payload

            async def __aenter__(self) -> Any:
                return self

            async def __aexit__(self, *a: Any) -> None:
                return None

            async def json(self, content_type: Any = None) -> dict:
                return self._payload

        sess = MagicMock()
        sess.post = MagicMock(side_effect=lambda *a, **k: _Resp(responses.pop(0)))
        bot._session = sess  # type: ignore[assignment]
        bot._get_session = AsyncMock(return_value=sess)  # type: ignore[method-assign]

        result = await bot._call("messages.send", peer_id=1)
        assert result == {"ok": 1}
        assert solved == ["S1"]

    async def test_timeout_is_configured(self) -> None:
        bot = Bot(token="t", timeout=12.5)
        assert isinstance(bot._timeout, aiohttp.ClientTimeout)
        assert bot._timeout.total == 12.5


class TestDedup:
    async def test_duplicate_event_id_processed_once(self) -> None:
        from fastvk.app import FastVK

        app = FastVK(token="t", group_id=1, throttle_rate=0)
        app.bot = MockedBot()  # type: ignore[assignment]
        hits: list[int] = []

        @app.message()
        async def h(message: Message) -> None:
            hits.append(message.id)

        upd = message_update("hi", event_id="dup-1")
        await app._process_update(upd)
        await app._process_update(upd)
        assert hits == [1]


# --------------------------------------------------------------------------
# 2. Filters / attachments / keyboard
# --------------------------------------------------------------------------


class _Msg:
    def __init__(self, text: str = "", attachments: list[dict] | None = None) -> None:
        self.text = text
        self.attachments = attachments or []

    @property
    def content_types(self) -> set[str]:
        t = {a.get("type", "") for a in self.attachments}
        t.discard("")
        if self.text:
            t.add("text")
        return t or {"text"}

    def has_attachment(self, *types: str) -> bool:
        if not self.attachments:
            return False
        if not types:
            return True
        return bool({a.get("type") for a in self.attachments} & set(types))


class TestNewFilters:
    def test_regexp_matches_and_injects(self) -> None:
        f = Regexp(r"^#(\d+)$")
        data: dict = {}
        assert f(_Msg("#42"), data) is True
        assert data[re.Match].group(1) == "42"

    def test_regexp_no_match(self) -> None:
        assert Regexp(r"^\d+$")(_Msg("abc"), {}) is False

    def test_content_type_photo(self) -> None:
        assert ContentType("photo")(_Msg("", [{"type": "photo"}]), {}) is True
        assert ContentType("photo")(_Msg("hi"), {}) is False

    def test_content_type_text(self) -> None:
        assert ContentType("text")(_Msg("hi"), {}) is True

    def test_has_attachment(self) -> None:
        assert HasAttachment()(_Msg("", [{"type": "doc"}]), {}) is True
        assert HasAttachment("photo")(_Msg("", [{"type": "doc"}]), {}) is False

    def test_command_ignore_case(self) -> None:
        f = Command("Start", ignore_case=True)
        assert f(_Msg("/START"), {}) is True
        data: dict = {}
        assert f(_Msg("/start KEEP"), data) is True


class TestTypedAttachments:
    def test_parse_photo_and_largest(self) -> None:
        raw = {
            "type": "photo",
            "photo": {
                "owner_id": -1,
                "id": 2,
                "sizes": [
                    {"type": "s", "url": "small", "width": 75, "height": 75},
                    {"type": "x", "url": "big", "width": 604, "height": 604},
                ],
            },
        }
        photo = parse_attachment(raw)
        assert isinstance(photo, Photo)
        assert photo.attachment_string == "photo-1_2"
        assert photo.largest is not None
        assert photo.largest.url == "big"
        assert photo.url == "big"

    def test_message_photos_helper(self, mock_bot: MagicMock) -> None:
        msg = Message.from_dict(
            {
                "id": 1,
                "date": 0,
                "peer_id": 1,
                "from_id": 1,
                "text": "",
                "attachments": [{"type": "photo", "photo": {"owner_id": 1, "id": 9}}],
            },
            mock_bot,
        )
        assert msg.content_type == "photo"
        assert len(msg.photos) == 1
        assert msg.has_attachment("photo") is True


class TestKeyboardAdditions:
    def test_vkapps_button(self) -> None:
        b = Button.vkapps("Open", app_id=123, hash="x")
        assert b["action"]["type"] == "open_app"
        assert b["action"]["app_id"] == 123

    def test_carousel_build(self) -> None:
        c = (
            Carousel()
            .element(title="A", buttons=[Button.callback("go", payload={"x": 1})], link="https://e.x")
            .element(title="B")
        )
        import json

        data = json.loads(c.build())
        assert data["type"] == "carousel"
        assert len(data["elements"]) == 2
        assert data["elements"][0]["action"] == {"type": "open_link", "link": "https://e.x"}

    def test_carousel_limit(self) -> None:
        c = Carousel()
        for _ in range(10):
            c.element(title="x")
        with pytest.raises(ValueError):
            c.element(title="overflow")


# --------------------------------------------------------------------------
# 3. Client extras
# --------------------------------------------------------------------------


class TestClientExtras:
    async def test_execute_batch_builds_vkscript(self) -> None:
        bot = MockedBot()
        bot.set_result("execute", ["a", "b"])
        out = await bot.execute_batch(
            [("users.get", {"user_ids": 1}), ("groups.getById", {"group_id": 2})]
        )
        assert out == ["a", "b"]
        call = bot.assert_called("execute")
        assert "API.users.get" in call.params["code"]
        assert call.params["code"].startswith("return [")

    async def test_execute_batch_rejects_over_25(self) -> None:
        bot = MockedBot()
        with pytest.raises(ValueError):
            await bot.execute_batch([("users.get", {})] * 26)

    async def test_download_writes_file(self, tmp_path: Any) -> None:
        bot = Bot(token="t")

        class _Resp:
            async def __aenter__(self) -> Any:
                return self

            async def __aexit__(self, *a: Any) -> None:
                return None

            def raise_for_status(self) -> None:
                return None

            async def read(self) -> bytes:
                return b"filedata"

        sess = MagicMock()
        sess.get = MagicMock(return_value=_Resp())
        bot._get_session = AsyncMock(return_value=sess)  # type: ignore[method-assign]

        dest = tmp_path / "f.bin"
        content = await bot.download("https://x/f.bin", dest=dest)
        assert content == b"filedata"
        assert dest.read_bytes() == b"filedata"


# --------------------------------------------------------------------------
# 4. Scheduler / metrics / lifecycle / test utils
# --------------------------------------------------------------------------


class TestScheduler:
    def test_parse_interval(self) -> None:
        assert _parse_interval(30) == 30.0
        assert _parse_interval("5m") == 300.0
        assert _parse_interval("2h") == 7200.0
        assert _parse_interval("1d") == 86400.0

    async def test_every_registers_job(self) -> None:
        s = Scheduler()

        @s.every("1m")
        async def job() -> None: ...

        assert len(s._jobs) == 1
        assert s._jobs[0].interval == 60.0

    async def test_job_runs_when_due(self) -> None:
        s = Scheduler()
        ran: list[int] = []

        s.add_job(lambda: ran.append(1), "1s")
        s._jobs[0].next_run = 0  # force due
        await s.start()
        await asyncio.sleep(1.1)
        await s.stop()
        assert ran


class TestMetrics:
    def test_render_prometheus(self) -> None:
        app = MagicMock()
        app._stats = {
            "total": 10,
            "handled": 8,
            "errors": 1,
            "by_type": {"message_new": 7, "message_event": 3},
            "started_at": None,
        }
        app._tasks = set()
        text = render_prometheus(app)
        assert "fastvk_updates_total 10" in text
        assert 'fastvk_updates_by_type_total{type="message_new"} 7' in text


class TestLifecycleHooks:
    async def test_startup_and_shutdown_called(self) -> None:
        router = Router()
        events: list[str] = []

        @router.startup
        async def on_up() -> None:
            events.append("up")

        @router.shutdown
        async def on_down() -> None:
            events.append("down")

        await router._emit_startup({})
        await router._emit_shutdown({})
        assert events == ["up", "down"]


class TestTestUtils:
    async def test_mockedbot_records_calls(self) -> None:
        router = Router()

        @router.message(Command("ping"))
        async def h(message: Message) -> None:
            await message.answer("pong")

        bot = MockedBot()
        handled = await dispatch(router, bot, message_update("/ping"))
        assert handled is True
        assert bot.sent_messages[0]["message"] == "pong"

    async def test_callback_update_helper(self) -> None:
        router = Router()
        seen: list[str] = []

        @router.callback()
        async def h(callback: Any) -> None:
            seen.append(callback.payload.get("a"))

        bot = MockedBot()
        await dispatch(router, bot, callback_update('{"a": "b"}'))
        assert seen == ["b"]


class TestUserLongPoll:
    def test_parses_new_message_event(self) -> None:
        from fastvk.polling.userlongpoll import UserLongPoller

        poller = UserLongPoller(api=MagicMock())
        upd = poller._to_update([4, 55, 0, 123, 1700000000, "hello", {}, {}])
        assert upd.type == "message_new"
        assert upd.object["message"]["from_id"] == 123
        assert upd.object["message"]["text"] == "hello"

    def test_parses_chat_sender_from_attach(self) -> None:
        from fastvk.polling.userlongpoll import UserLongPoller

        poller = UserLongPoller(api=MagicMock())
        upd = poller._to_update(
            [4, 1, 0, 2000000001, 0, "hi", {}, {"from": "777"}]
        )
        assert upd.object["message"]["from_id"] == 777
