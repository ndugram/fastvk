from __future__ import annotations

from io import BytesIO
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from fastvk import Uploader
from fastvk.api.client import Bot


@pytest.mark.parametrize(
    ("method", "saved_type", "prefix"),
    [
        ("photo", "photo", "photo"),
        ("document", "doc", "doc"),
        ("audio_message", "audio_message", "doc"),
        ("graffiti", "graffiti", "doc"),
    ],
)
@pytest.mark.parametrize(
    "access_key",
    [{}, {"access_key": None}, {"access_key": ""}, {"access_key": "secret"}],
)
async def test_uploaded_attachment_can_be_sent_with_its_access_key(
    method: str,
    saved_type: str,
    prefix: str,
    access_key: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saved = {"owner_id": -123, "id": 456, **access_key}
    if method == "photo":
        uploaded: dict[str, Any] = {"photo": "uploaded-photo", "server": 1, "hash": "hash"}
        save_response: Any = [saved]
    else:
        uploaded = {"file": "uploaded-file"}
        save_response = {"type": saved_type, saved_type: saved}

    responses = [
        {"response": {"upload_url": "https://upload.example.test"}},
        uploaded,
        {"response": save_response},
        {"response": 1},
    ]
    requests = []
    for body in responses:
        response = MagicMock()
        response.status = 200
        response.json = AsyncMock(return_value=body)
        request = MagicMock()
        request.__aenter__ = AsyncMock(return_value=response)
        requests.append(request)

    session = MagicMock()
    session.post.side_effect = requests
    bot = Bot(token="test-token")
    monkeypatch.setattr(bot, "_get_session", AsyncMock(return_value=session))

    attachment = await getattr(Uploader(bot), method)(
        peer_id=42,
        file=BytesIO(b"media"),
        filename="media.bin",
    )
    expected = f"{prefix}-123_456_secret" if access_key.get("access_key") else f"{prefix}-123_456"
    assert attachment == expected

    await bot.messages.send(peer_id=42, message="Media", attachment=attachment)
    assert session.post.call_args.kwargs["data"]["attachment"] == expected
