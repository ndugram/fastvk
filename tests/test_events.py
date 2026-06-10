from __future__ import annotations

import pytest

from fastvk.types.events import GroupJoinEvent, GroupLeaveEvent, WallPostEvent


class TestGroupJoinEvent:
    def test_from_dict_basic(self) -> None:
        evt = GroupJoinEvent.from_dict({"user_id": 123, "join_type": "join"})
        assert evt.user_id == 123
        assert evt.join_type == "join"

    def test_from_dict_default_join_type(self) -> None:
        evt = GroupJoinEvent.from_dict({"user_id": 456})
        assert evt.join_type == "join"

    def test_join_type_invite(self) -> None:
        evt = GroupJoinEvent.from_dict({"user_id": 1, "join_type": "invite"})
        assert evt.join_type == "invite"

    def test_join_type_request(self) -> None:
        evt = GroupJoinEvent.from_dict({"user_id": 1, "join_type": "request"})
        assert evt.join_type == "request"

    def test_is_frozen(self) -> None:
        evt = GroupJoinEvent.from_dict({"user_id": 1, "join_type": "join"})
        with pytest.raises(Exception):
            evt.user_id = 999  # type: ignore[misc]


class TestGroupLeaveEvent:
    def test_from_dict_self_leave(self) -> None:
        evt = GroupLeaveEvent.from_dict({"user_id": 123, "self": 1})
        assert evt.user_id == 123
        assert evt.is_self is True

    def test_from_dict_kicked(self) -> None:
        evt = GroupLeaveEvent.from_dict({"user_id": 123, "self": 0})
        assert evt.is_self is False

    def test_from_dict_default_is_self_false(self) -> None:
        evt = GroupLeaveEvent.from_dict({"user_id": 123})
        assert evt.is_self is False

    def test_is_frozen(self) -> None:
        evt = GroupLeaveEvent.from_dict({"user_id": 1, "self": 0})
        with pytest.raises(Exception):
            evt.user_id = 999  # type: ignore[misc]


class TestWallPostEvent:
    _base: dict = {
        "id": 42,
        "owner_id": -100500,
        "from_id": 123456,
        "date": 1700000000,
        "text": "Hello, world!",
        "post_type": "post",
    }

    def test_from_dict_basic(self) -> None:
        evt = WallPostEvent.from_dict(self._base)
        assert evt.id == 42
        assert evt.owner_id == -100500
        assert evt.from_id == 123456
        assert evt.text == "Hello, world!"
        assert evt.post_type == "post"

    def test_from_dict_default_text(self) -> None:
        data = {**self._base, "text": ""}
        evt = WallPostEvent.from_dict(data)
        assert evt.text == ""

    def test_from_dict_default_post_type(self) -> None:
        data = {k: v for k, v in self._base.items() if k != "post_type"}
        evt = WallPostEvent.from_dict(data)
        assert evt.post_type == "post"

    def test_from_dict_attachments(self) -> None:
        data = {**self._base, "attachments": [{"type": "photo"}]}
        evt = WallPostEvent.from_dict(data)
        assert len(evt.attachments) == 1
        assert evt.attachments[0]["type"] == "photo"

    def test_from_dict_empty_attachments_by_default(self) -> None:
        evt = WallPostEvent.from_dict(self._base)
        assert evt.attachments == []

    def test_raw_preserved(self) -> None:
        evt = WallPostEvent.from_dict(self._base)
        assert evt.raw["id"] == 42

    def test_from_id_falls_back_to_owner_id(self) -> None:
        data = {k: v for k, v in self._base.items() if k != "from_id"}
        evt = WallPostEvent.from_dict(data)
        assert evt.from_id == data["owner_id"]

    def test_is_frozen(self) -> None:
        evt = WallPostEvent.from_dict(self._base)
        with pytest.raises(Exception):
            evt.id = 999  # type: ignore[misc]
