from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


from fastvk.api.client import Bot
from fastvk.fsm.storage import MemoryStorage
from fastvk.types.callback import CallbackQuery
from fastvk.types.message import Message
from fastvk.types.update import Update
from fastvk.types.user import User


@pytest.fixture
def mock_bot() -> MagicMock:
    bot = MagicMock(spec=Bot)
    bot._call = AsyncMock(return_value=None)
    bot.messages = MagicMock()
    bot.messages.send = AsyncMock(return_value=1)
    bot.messages.sendMessageEventAnswer = AsyncMock(return_value=1)
    bot.users = MagicMock()
    bot.users.get = AsyncMock(
        return_value=[{"id": 123456, "first_name": "Иван", "last_name": "Петров"}]
    )
    return bot


@pytest.fixture
def storage() -> MemoryStorage:
    return MemoryStorage()


@pytest.fixture
def sample_user() -> User:
    return User(id=123456, first_name="Иван", last_name="Петров")


@pytest.fixture
def make_message(mock_bot: MagicMock) -> Any:
    def _make(
        text: str = "Привет",
        from_id: int = 123456,
        peer_id: int = 123456,
        msg_id: int = 1,
    ) -> Message:
        return Message.from_dict(
            {
                "id": msg_id,
                "date": 1700000000,
                "peer_id": peer_id,
                "from_id": from_id,
                "text": text,
            },
            mock_bot,
        )

    return _make


@pytest.fixture
def make_update() -> Any:
    def _make(
        event_type: str = "message_new",
        obj: dict | None = None,
        group_id: int = 1,
        event_id: str = "abc123",
    ) -> Update:
        if obj is None:
            obj = {
                "message": {
                    "id": 1,
                    "date": 1700000000,
                    "peer_id": 123456,
                    "from_id": 123456,
                    "text": "Привет",
                }
            }
        return Update(type=event_type, object=obj, group_id=group_id, event_id=event_id)

    return _make


@pytest.fixture
def make_callback(mock_bot: MagicMock) -> Any:
    def _make(
        user_id: int = 123456,
        peer_id: int = 123456,
        payload: str = '{"cmd": "test"}',
    ) -> CallbackQuery:
        return CallbackQuery.from_dict(
            {
                "user_id": user_id,
                "peer_id": peer_id,
                "event_id": "evt_1",
                "payload": payload,
                "conversation_message_id": 10,
            },
            mock_bot,
        )

    return _make
