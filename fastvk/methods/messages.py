from __future__ import annotations

import random

from pydantic import Field

from .base import VKMethod


class MessagesSend(VKMethod[int]):
    """Send a message. Returns the sent message ID."""

    __returning__ = int
    __api_method__ = "messages.send"

    peer_id: int
    message: str
    random_id: int = Field(default_factory=lambda: random.randint(0, 2**31))
    keyboard: str | None = None
    attachment: str | None = None
    reply_to: int | None = None
    dont_parse_links: int | None = None
    disable_mentions: int | None = None


class MessagesDelete(VKMethod[dict]):
    """Delete messages by IDs."""

    __returning__ = dict
    __api_method__ = "messages.delete"

    message_ids: int | str
    delete_for_all: int = 0
    peer_id: int | None = None


class MessagesGetById(VKMethod[dict]):
    """Get messages by IDs."""

    __returning__ = dict
    __api_method__ = "messages.getById"

    message_ids: int | str
    extended: int = 0


class MessagesSendEventAnswer(VKMethod[int]):
    """Answer a callback button press (message_event)."""

    __returning__ = int
    __api_method__ = "messages.sendMessageEventAnswer"

    event_id: str
    user_id: int
    peer_id: int
    event_data: str | None = None


class MessagesGetLongPollServer(VKMethod[dict]):
    """Get Long Poll server parameters."""

    __returning__ = dict
    __api_method__ = "groups.getLongPollServer"

    group_id: int
    lp_version: int = 3


class MessagesGetConversations(VKMethod[dict]):
    """Get conversations list."""

    __returning__ = dict
    __api_method__ = "messages.getConversations"

    offset: int = 0
    count: int = 20
    filter: str = "all"
    extended: int = 0


class MessagesPin(VKMethod[dict]):
    """Pin a message in a conversation. Returns the pinned message object."""

    __returning__ = dict
    __api_method__ = "messages.pin"

    peer_id: int
    message_id: int | None = None
    conversation_message_id: int | None = None


class MessagesUnpin(VKMethod[int]):
    """Unpin a message in a conversation. Returns 1 on success."""

    __returning__ = int
    __api_method__ = "messages.unpin"

    peer_id: int


class MessagesMarkAsRead(VKMethod[int]):
    """Mark messages as read. Returns 1 on success."""

    __returning__ = int
    __api_method__ = "messages.markAsRead"

    peer_id: int | None = None
    message_ids: str | None = None
    start_message_id: int | None = None


class MessagesGetHistory(VKMethod[dict]):
    """Get message history for a conversation."""

    __returning__ = dict
    __api_method__ = "messages.getHistory"

    peer_id: int
    offset: int = 0
    count: int = 20
    start_message_id: int | None = None
    rev: int = 0
    extended: int = 0


class MessagesEdit(VKMethod[int]):
    """Edit a previously sent message. Returns 1 on success."""

    __returning__ = int
    __api_method__ = "messages.edit"

    peer_id: int
    message_id: int
    message: str
    attachment: str | None = None
    keyboard: str | None = None
    dont_parse_links: int | None = None
    disable_mentions: int | None = None


class MessagesSetActivity(VKMethod[int]):
    """Send a chat action indicator (typing, recording audio, etc.)."""

    __returning__ = int
    __api_method__ = "messages.setActivity"

    peer_id: int
    type: str = "typing"
