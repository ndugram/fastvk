from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from fastvk.api.client import Bot
from fastvk.keyboard import Carousel
from fastvk.methods import MessagesDelete, MessagesEdit, MessagesSend
from fastvk.types.callback import CallbackQuery
from fastvk.types.message import Message


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch) -> tuple[Bot, MagicMock, MagicMock]:
    bot = Bot("test-token", max_retries=0)
    response = MagicMock()
    response.json = AsyncMock(return_value={"response": 1})
    session = MagicMock()
    session.post.return_value.__aenter__.return_value = response
    monkeypatch.setattr(bot, "_get_session", AsyncMock(return_value=session))
    return bot, session, response


def incoming_message(bot: Bot, **overrides: Any) -> Message:
    return Message.from_dict(
        {
            "id": 1000,
            "conversation_message_id": 7,
            "date": 1700000000,
            "peer_id": 42,
            "from_id": 42,
            **overrides,
        },
        bot,
    )


@pytest.mark.parametrize(
    ("recipient", "encoded"),
    [
        ({"peer_id": 42}, {"peer_id": 42}),
        ({"peer_ids": [42, 43]}, {"peer_ids": "42,43"}),
        ({"peer_ids": "42,43"}, {"peer_ids": "42,43"}),
        ({"user_id": 42}, {"user_id": 42}),
        ({"chat_id": 5}, {"chat_id": 5}),
        ({"domain": "test_user"}, {"domain": "test_user"}),
    ],
)
async def test_send_supports_alternative_recipients(
    api: tuple[Bot, MagicMock, MagicMock],
    recipient: dict[str, Any],
    encoded: dict[str, Any],
) -> None:
    bot, session, _ = api
    await bot.messages.send(**recipient, message="Hello", random_id=123)

    params = session.post.call_args.kwargs["data"]
    assert {key: params[key] for key in encoded} == encoded
    if "peer_id" not in recipient:
        assert "peer_id" not in params
    assert params["message"] == "Hello"
    assert params["random_id"] == 123


async def test_typed_send_preserves_per_recipient_results(
    api: tuple[Bot, MagicMock, MagicMock],
) -> None:
    bot, session, response = api
    results = [
        {"peer_id": 42, "message_id": 1000, "conversation_message_id": 7},
        {"peer_id": 43, "error": {"error_code": 901, "error_msg": "Cannot send"}},
    ]
    response.json.return_value = {"response": results}

    result = await bot(MessagesSend(peer_ids=[42, 43], attachment="photo-1_2"))

    assert result == results
    params = session.post.call_args.kwargs["data"]
    assert params["attachment"] == "photo-1_2"
    assert "message" not in params


async def test_answer_sticker_does_not_require_text(
    api: tuple[Bot, MagicMock, MagicMock],
) -> None:
    bot, session, _ = api
    assert await incoming_message(bot).answer_sticker(9001) == 1
    params = session.post.call_args.kwargs["data"]
    assert params["sticker_id"] == 9001
    assert "message" not in params


async def test_answer_carousel_preserves_template(
    api: tuple[Bot, MagicMock, MagicMock],
) -> None:
    bot, session, _ = api
    carousel = Carousel().element(title="House", photo_id="-1_2")
    await incoming_message(bot).answer_carousel(carousel)
    assert session.post.call_args.kwargs["data"]["template"] == str(carousel)


@pytest.mark.parametrize(
    ("selector", "encoded"),
    [
        ({"message_id": 1000}, {"message_id": 1000}),
        ({"cmid": 7}, {"cmid": 7}),
        ({"conversation_message_id": 7}, {"cmid": 7}),
        ({"cmid": 7, "conversation_message_id": 7}, {"cmid": 7}),
    ],
)
async def test_edit_supports_global_and_conversation_message_ids(
    api: tuple[Bot, MagicMock, MagicMock],
    selector: dict[str, Any],
    encoded: dict[str, Any],
) -> None:
    bot, session, _ = api
    await bot.messages.edit(peer_id=42, attachment="photo-1_2", **selector)
    params = session.post.call_args.kwargs["data"]
    assert {key: params[key] for key in encoded} == encoded
    assert "conversation_message_id" not in params
    assert "message" not in params
    if "message_id" not in selector:
        assert "message_id" not in params


def test_edit_rejects_conflicting_cmid_aliases() -> None:
    with pytest.raises(ValueError, match="cmid"):
        MessagesEdit(peer_id=42, cmid=7, conversation_message_id=8, message="Text")


async def test_callback_edit_uses_its_conversation_message_id(
    api: tuple[Bot, MagicMock, MagicMock],
) -> None:
    bot, session, _ = api
    callback = CallbackQuery.from_dict(
        {"user_id": 42, "peer_id": 42, "event_id": "event", "conversation_message_id": 7},
        bot,
    )
    assert await callback.edit_message("Updated") == 1
    params = session.post.call_args.kwargs["data"]
    assert params["cmid"] == 7
    assert "message_id" not in params


@pytest.mark.parametrize(
    ("selector", "encoded"),
    [
        ({"message_ids": 1000}, {"message_ids": 1000}),
        ({"message_ids": [1000, 1001]}, {"message_ids": "1000,1001"}),
        ({"message_ids": "1000,1001"}, {"message_ids": "1000,1001"}),
        ({"peer_id": 42, "cmids": 7}, {"peer_id": 42, "cmids": 7}),
        ({"peer_id": 42, "cmids": [7, 8]}, {"peer_id": 42, "cmids": "7,8"}),
        ({"peer_id": 42, "cmids": "7,8"}, {"peer_id": 42, "cmids": "7,8"}),
    ],
)
async def test_delete_supports_global_and_conversation_message_ids(
    api: tuple[Bot, MagicMock, MagicMock],
    selector: dict[str, Any],
    encoded: dict[str, Any],
) -> None:
    bot, session, response = api
    response.json.return_value = {"response": {"7": 1}}
    assert await MessagesDelete(delete_for_all=1, **selector).emit(bot) == {"7": 1}
    params = session.post.call_args.kwargs["data"]
    assert {key: params[key] for key in encoded} == encoded
    if "message_ids" not in selector:
        assert "message_ids" not in params


async def test_message_lookup_uses_conversation_message_id_instead_of_global_id(
    api: tuple[Bot, MagicMock, MagicMock],
) -> None:
    bot, session, response = api
    response.json.return_value = {"response": {"items": []}}
    message = incoming_message(bot)
    assert message.conversation_message_id == 7
    assert await message.get_by_conversation_message_id() == {"items": []}
    assert session.post.call_args.kwargs["data"]["conversation_message_ids"] == "7"


async def test_message_lookup_does_not_guess_missing_conversation_message_id(
    api: tuple[Bot, MagicMock, MagicMock],
) -> None:
    bot, session, _ = api
    message = incoming_message(bot, conversation_message_id=None)
    with pytest.raises(ValueError, match="conversation_message_id"):
        await message.get_by_conversation_message_id()
    session.post.assert_not_called()
