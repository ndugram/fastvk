from __future__ import annotations

from .base import VKMethod


class UsersGet(VKMethod[list]):
    """Get user profiles. Returns list of user dicts."""

    __returning__ = list
    __api_method__ = "users.get"

    user_ids: int | str | None = None
    fields: str | None = None
    name_case: str | None = None


class UsersSearch(VKMethod[dict]):
    """Search for users."""

    __returning__ = dict
    __api_method__ = "users.search"

    q: str | None = None
    count: int = 20
    offset: int = 0
    fields: str | None = None
