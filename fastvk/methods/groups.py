from __future__ import annotations

from .base import VKMethod


class GroupsGetLongPollServer(VKMethod[dict]):
    """Get Long Poll server for a group."""

    __returning__ = dict
    __api_method__ = "groups.getLongPollServer"

    group_id: int


class GroupsGetById(VKMethod[list]):
    """Get group info by ID."""

    __returning__ = list
    __api_method__ = "groups.getById"

    group_id: int | str | None = None
    fields: str | None = None


class GroupsGetMembers(VKMethod[dict]):
    """Get group members."""

    __returning__ = dict
    __api_method__ = "groups.getMembers"

    group_id: int | str | None = None
    count: int = 100
    offset: int = 0
    fields: str | None = None
    filter: str | None = None
