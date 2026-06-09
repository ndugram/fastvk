from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock


from fastvk.types.callback import CallbackQuery
from fastvk.types.group import Group
from fastvk.types.message import Message
from fastvk.types.user import User


class TestMessage:
    def test_from_dict_basic(self, make_message: Any) -> None:
        msg = make_message(text="Тест", from_id=111, peer_id=222)
        assert msg.text == "Тест"
        assert msg.from_id == 111
        assert msg.peer_id == 222

    def test_from_dict_defaults(self, mock_bot: MagicMock) -> None:
        msg = Message.from_dict(
            {"id": 5, "date": 1700000000, "peer_id": 1, "from_id": 1},
            mock_bot,
        )
        assert msg.text == ""
        assert msg.attachments == []
        assert msg.fwd_messages == []
        assert msg.payload is None

    def test_bot_attached(self, make_message: Any, mock_bot: MagicMock) -> None:
        msg = make_message()
        assert msg._bot is mock_bot

    def test_from_user_initially_none(self, make_message: Any) -> None:
        msg = make_message()
        assert msg.from_user is None

    def test_from_user_set(self, make_message: Any) -> None:
        msg = make_message()
        user = User(id=1, first_name="Иван", last_name="Петров")
        msg._from_user = user
        assert msg.from_user is user

    def test_is_private_true(self, make_message: Any) -> None:
        msg = make_message(peer_id=123456)
        assert msg.is_private is True
        assert msg.is_chat is False

    def test_is_chat_true(self, make_message: Any) -> None:
        msg = make_message(peer_id=2_000_000_001)
        assert msg.is_chat is True
        assert msg.is_private is False

    def test_chat_id(self, make_message: Any) -> None:
        msg = make_message(peer_id=2_000_000_005)
        assert msg.chat_id == 5

    def test_chat_id_none_for_private(self, make_message: Any) -> None:
        msg = make_message(peer_id=123456)
        assert msg.chat_id is None

    async def test_answer_calls_bot(self, make_message: Any, mock_bot: MagicMock) -> None:
        msg = make_message(peer_id=111)
        await msg.answer("Привет")
        mock_bot.messages.send.assert_awaited_once()
        call_kwargs = mock_bot.messages.send.call_args.kwargs
        assert call_kwargs["peer_id"] == 111
        assert call_kwargs["message"] == "Привет"

    async def test_reply_includes_reply_to(self, make_message: Any, mock_bot: MagicMock) -> None:
        msg = make_message(msg_id=42, peer_id=111)
        await msg.reply("Ответ")
        call_kwargs = mock_bot.messages.send.call_args.kwargs
        assert call_kwargs["reply_to"] == 42

    async def test_answer_photo(self, make_message: Any, mock_bot: MagicMock) -> None:
        msg = make_message(peer_id=111)
        await msg.answer_photo("photo-1_2", caption="Красиво")
        call_kwargs = mock_bot.messages.send.call_args.kwargs
        assert call_kwargs["attachment"] == "photo-1_2"
        assert call_kwargs["message"] == "Красиво"

    async def test_answer_doc(self, make_message: Any, mock_bot: MagicMock) -> None:
        msg = make_message(peer_id=111)
        await msg.answer_doc("doc-1_2")
        call_kwargs = mock_bot.messages.send.call_args.kwargs
        assert call_kwargs["attachment"] == "doc-1_2"

    async def test_answer_video(self, make_message: Any, mock_bot: MagicMock) -> None:
        msg = make_message(peer_id=111)
        await msg.answer_video("video-1_2")
        call_kwargs = mock_bot.messages.send.call_args.kwargs
        assert call_kwargs["attachment"] == "video-1_2"

    async def test_answer_sticker(self, make_message: Any, mock_bot: MagicMock) -> None:
        msg = make_message(peer_id=111)
        await msg.answer_sticker(9001)
        call_kwargs = mock_bot.messages.send.call_args.kwargs
        assert call_kwargs["sticker_id"] == 9001

    async def test_forward_same_peer(self, make_message: Any, mock_bot: MagicMock) -> None:
        msg = make_message(msg_id=7, peer_id=111)
        await msg.forward()
        call_kwargs = mock_bot.messages.send.call_args.kwargs
        assert call_kwargs["forward_messages"] == 7
        assert call_kwargs["peer_id"] == 111

    async def test_forward_different_peer(self, make_message: Any, mock_bot: MagicMock) -> None:
        msg = make_message(msg_id=7, peer_id=111)
        await msg.forward(peer_id=999)
        call_kwargs = mock_bot.messages.send.call_args.kwargs
        assert call_kwargs["peer_id"] == 999


class TestUser:
    def test_from_dict(self) -> None:
        user = User.from_dict({"id": 1, "first_name": "Иван", "last_name": "Петров"})
        assert user.id == 1
        assert user.first_name == "Иван"
        assert user.last_name == "Петров"

    def test_full_name(self) -> None:
        user = User(id=1, first_name="Иван", last_name="Петров")
        assert user.full_name == "Иван Петров"

    def test_from_dict_missing_names(self) -> None:
        user = User.from_dict({"id": 42})
        assert user.first_name == ""
        assert user.last_name == ""

    def test_pydantic_model(self) -> None:
        user = User(id=1, first_name="A", last_name="B")
        d = user.model_dump()
        assert d["id"] == 1
        assert d["first_name"] == "A"


class TestGroup:
    def test_from_dict(self) -> None:
        group = Group.from_dict(
            {"id": 1, "name": "Test Group", "screen_name": "testgroup", "members_count": 1000}
        )
        assert group.id == 1
        assert group.name == "Test Group"
        assert group.screen_name == "testgroup"
        assert group.members_count == 1000

    def test_from_dict_defaults(self) -> None:
        group = Group.from_dict({"id": 1, "name": "G", "screen_name": "g"})
        assert group.photo_50 == ""
        assert group.description == ""
        assert group.members_count == 0

    def test_mention(self) -> None:
        group = Group(id=1, name="G", screen_name="mygroup")
        assert group.mention == "@mygroup"

    def test_url(self) -> None:
        group = Group(id=1, name="G", screen_name="mygroup")
        assert group.url == "https://vk.com/mygroup"


class TestCallbackQuery:
    def test_from_dict_json_payload(self, make_callback: Any) -> None:
        cb = make_callback(payload='{"cmd": "like"}')
        assert cb.payload == {"cmd": "like"}

    def test_from_dict_dict_payload(self, mock_bot: MagicMock) -> None:
        cb = CallbackQuery.from_dict(
            {
                "user_id": 1,
                "peer_id": 1,
                "event_id": "e1",
                "payload": {"cmd": "already_dict"},
                "conversation_message_id": 0,
            },
            mock_bot,
        )
        assert cb.payload == {"cmd": "already_dict"}

    def test_from_dict_invalid_payload_defaults_empty(self, mock_bot: MagicMock) -> None:
        cb = CallbackQuery.from_dict(
            {
                "user_id": 1,
                "peer_id": 1,
                "event_id": "e1",
                "payload": "not json{{",
                "conversation_message_id": 0,
            },
            mock_bot,
        )
        assert cb.payload == {}

    def test_from_dict_no_payload(self, mock_bot: MagicMock) -> None:
        cb = CallbackQuery.from_dict(
            {"user_id": 1, "peer_id": 1, "event_id": "e1", "conversation_message_id": 0},
            mock_bot,
        )
        assert cb.payload == {}

    def test_user_and_peer_set(self, make_callback: Any) -> None:
        cb = make_callback(user_id=111, peer_id=222)
        assert cb.user_id == 111
        assert cb.peer_id == 222

    async def test_answer_snackbar(self, make_callback: Any, mock_bot: MagicMock) -> None:
        cb = make_callback()
        await cb.answer("Готово!")
        mock_bot.messages.sendMessageEventAnswer.assert_awaited_once()
