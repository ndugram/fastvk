from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class GroupJoinEvent(BaseModel):
    """Fired when a user joins the group (``group_join`` event)."""

    model_config = ConfigDict(frozen=True)

    user_id: int
    join_type: Literal["join", "unsure", "accepted", "approved", "link", "invite", "request"] | str = "join"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GroupJoinEvent:
        return cls(
            user_id=data["user_id"],
            join_type=data.get("join_type", "join"),
        )


class GroupLeaveEvent(BaseModel):
    """Fired when a user leaves the group (``group_leave`` event)."""

    model_config = ConfigDict(frozen=True)

    user_id: int
    is_self: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GroupLeaveEvent:
        return cls(
            user_id=data["user_id"],
            is_self=bool(data.get("self", 0)),
        )


class WallPostEvent(BaseModel):
    """Fired when a new wall post is created (``wall_post_new`` event)."""

    model_config = ConfigDict(frozen=True)

    id: int
    owner_id: int
    from_id: int
    date: int
    text: str = ""
    post_type: str = "post"
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WallPostEvent:
        return cls(
            id=data["id"],
            owner_id=data["owner_id"],
            from_id=data.get("from_id", data["owner_id"]),
            date=data["date"],
            text=data.get("text", ""),
            post_type=data.get("post_type", "post"),
            attachments=data.get("attachments", []),
            raw=data,
        )
