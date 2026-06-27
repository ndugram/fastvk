from __future__ import annotations

from .base import VKMethod


class WallPost(VKMethod[dict]):
    """Publish a post on a wall. Returns dict with ``post_id``."""

    __returning__ = dict
    __api_method__ = "wall.post"

    owner_id: int | None = None
    message: str | None = None
    attachments: str | None = None
    from_group: int = 0
    signed: int = 0
    publish_date: int | None = None


class WallGet(VKMethod[dict]):
    """Get wall posts. Supports pagination via ``count`` / ``offset``."""

    __returning__ = dict
    __api_method__ = "wall.get"

    owner_id: int | None = None
    domain: str | None = None
    offset: int = 0
    count: int = 20
    filter: str | None = None
    extended: int = 0
    fields: str | None = None


class WallGetById(VKMethod[list]):
    """Get wall posts by IDs. ``posts`` — comma-separated ``owner_id_post_id`` list."""

    __returning__ = list
    __api_method__ = "wall.getById"

    posts: str
    extended: int = 0
