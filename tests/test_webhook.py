from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from fastvk.types.update import Update
from fastvk.webhook import WebhookHandler


def _make_app_mock(group_id: int = 1) -> MagicMock:
    app = MagicMock()
    app.group_id = group_id
    app._process_update = AsyncMock()
    return app


async def _make_client(handler: WebhookHandler) -> TestClient:
    aioapp = web.Application()
    aioapp.router.add_post("/", handler.handle)
    client = TestClient(TestServer(aioapp))
    await client.start_server()
    return client


class TestWebhookConfirmation:
    async def test_returns_confirmation_token(self) -> None:
        mock_app = _make_app_mock()
        handler = WebhookHandler(mock_app, confirmation_token="abc123")
        client = await _make_client(handler)

        resp = await client.post("/", json={"type": "confirmation", "group_id": 1})
        assert resp.status == 200
        text = await resp.text()
        assert text == "abc123"

        await client.close()

    async def test_confirmation_not_json_object(self) -> None:
        mock_app = _make_app_mock()
        handler = WebhookHandler(mock_app, confirmation_token="xyz")
        client = await _make_client(handler)

        resp = await client.post("/", data="not json", headers={"Content-Type": "application/json"})
        assert resp.status == 400

        await client.close()


class TestWebhookSecret:
    async def test_correct_secret_passes(self) -> None:
        mock_app = _make_app_mock()
        handler = WebhookHandler(mock_app, confirmation_token="tok", secret="s3cr3t")
        client = await _make_client(handler)

        resp = await client.post(
            "/",
            json={"type": "confirmation", "group_id": 1, "secret": "s3cr3t"},
        )
        assert resp.status == 200
        assert await resp.text() == "tok"

        await client.close()

    async def test_wrong_secret_rejected(self) -> None:
        mock_app = _make_app_mock()
        handler = WebhookHandler(mock_app, confirmation_token="tok", secret="s3cr3t")
        client = await _make_client(handler)

        resp = await client.post(
            "/",
            json={"type": "message_new", "object": {}, "group_id": 1, "event_id": "e1", "secret": "WRONG"},
        )
        assert resp.status == 403

        await client.close()

    async def test_missing_secret_rejected(self) -> None:
        mock_app = _make_app_mock()
        handler = WebhookHandler(mock_app, confirmation_token="tok", secret="s3cr3t")
        client = await _make_client(handler)

        resp = await client.post(
            "/",
            json={"type": "message_new", "object": {}, "group_id": 1, "event_id": "e1"},
        )
        assert resp.status == 403

        await client.close()

    async def test_no_secret_configured_any_request_passes(self) -> None:
        mock_app = _make_app_mock()
        handler = WebhookHandler(mock_app, confirmation_token="tok")
        client = await _make_client(handler)

        resp = await client.post(
            "/",
            json={
                "type": "message_new",
                "object": {"message": {"id": 1, "date": 0, "peer_id": 1, "from_id": 1, "text": "hi"}},
                "group_id": 1,
                "event_id": "e1",
            },
        )
        assert resp.status == 200

        await client.close()


class TestWebhookUpdateDispatch:
    async def test_returns_ok_for_known_event(self) -> None:
        mock_app = _make_app_mock()
        handler = WebhookHandler(mock_app, confirmation_token="tok")
        client = await _make_client(handler)

        resp = await client.post(
            "/",
            json={
                "type": "message_new",
                "object": {"message": {"id": 1, "date": 0, "peer_id": 1, "from_id": 1, "text": "hi"}},
                "group_id": 1,
                "event_id": "evt_1",
            },
        )
        assert resp.status == 200
        assert await resp.text() == "ok"

        await client.close()

    async def test_process_update_called(self) -> None:
        mock_app = _make_app_mock()
        handler = WebhookHandler(mock_app, confirmation_token="tok")
        client = await _make_client(handler)

        await client.post(
            "/",
            json={
                "type": "message_new",
                "object": {"message": {"id": 1, "date": 0, "peer_id": 1, "from_id": 1, "text": "hi"}},
                "group_id": 1,
                "event_id": "evt_1",
            },
        )
        await asyncio.sleep(0.05)
        mock_app._process_update.assert_called_once()

        update: Update = mock_app._process_update.call_args[0][0]
        assert update.type == "message_new"
        assert update.event_id == "evt_1"
        assert update.group_id == 1

        await client.close()

    async def test_group_id_fallback(self) -> None:
        mock_app = _make_app_mock(group_id=42)
        handler = WebhookHandler(mock_app, confirmation_token="tok")
        client = await _make_client(handler)

        await client.post(
            "/",
            json={
                "type": "wall_post_new",
                "object": {},
                "event_id": "e2",
            },
        )
        await asyncio.sleep(0.05)
        update: Update = mock_app._process_update.call_args[0][0]
        assert update.group_id == 42

        await client.close()

    async def test_malformed_update_does_not_crash(self) -> None:
        mock_app = _make_app_mock()
        handler = WebhookHandler(mock_app, confirmation_token="tok")
        client = await _make_client(handler)

        resp = await client.post("/", json={"type": "broken_event"})
        assert resp.status == 200
        assert await resp.text() == "ok"

        await client.close()
