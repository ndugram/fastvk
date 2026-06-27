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
    sticker_id: int | None = None
    payload: str | None = None
    forward_messages: int | str | None = None
    forward: str | None = None
    content_source: str | None = None
    intent: str | None = None
    subscribe_id: int | None = None


class MessagesDelete(VKMethod[dict]):
    """Delete messages by IDs."""

    __returning__ = dict
    __api_method__ = "messages.delete"

    message_ids: int | str
    delete_for_all: int = 0
    peer_id: int | None = None
    cmids: int | str | None = None
    spam: int = 0


class MessagesGetById(VKMethod[dict]):
    """Get messages by IDs."""

    __returning__ = dict
    __api_method__ = "messages.getById"

    message_ids: int | str
    extended: int = 0
    fields: str | None = None
    preview_length: int | None = None


class MessagesSendEventAnswer(VKMethod[int]):
    """Answer a callback button press (message_event)."""

    __returning__ = int
    __api_method__ = "messages.sendMessageEventAnswer"

    event_id: str
    user_id: int
    peer_id: int
    event_data: str | None = None


class MessagesGetConversations(VKMethod[dict]):
    """Get conversations list."""

    __returning__ = dict
    __api_method__ = "messages.getConversations"

    offset: int = 0
    count: int = 20
    filter: str = "all"
    extended: int = 0
    start_message_id: int | None = None
    fields: str | None = None
    group_id: int | None = None


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
    fields: str | None = None
    group_id: int | None = None


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
    content_source: str | None = None
    template: str | None = None
    keep_forward_messages: int = 0
    keep_snippets: int = 0


class MessagesSetActivity(VKMethod[int]):
    """Send a chat action indicator (typing, recording audio, etc.)."""

    __returning__ = int
    __api_method__ = "messages.setActivity"

    peer_id: int
    type: str = "typing"
    group_id: int | None = None


class MessagesSearch(VKMethod[dict]):
    """Search messages. Returns paginated results."""

    __returning__ = dict
    __api_method__ = "messages.search"

    q: str
    peer_id: int | None = None
    date: int | None = None
    preview_length: int = 0
    offset: int = 0
    count: int = 20
    extended: int = 0
    fields: str | None = None
    group_id: int | None = None


class MessagesGetChat(VKMethod[dict]):
    """Get chat info by chat ID."""

    __returning__ = dict
    __api_method__ = "messages.getChat"

    chat_id: int
    fields: str | None = None
    name_case: str | None = None


class MessagesCreateChat(VKMethod[int]):
    """Create a new chat. Returns the chat ID."""

    __returning__ = int
    __api_method__ = "messages.createChat"

    title: str
    peer_ids: list[int] | None = None
    group_id: int | None = None


class MessagesEditChat(VKMethod[int]):
    """Edit chat title."""

    __returning__ = int
    __api_method__ = "messages.editChat"

    chat_id: int
    title: str


class MessagesAddChatUser(VKMethod[int]):
    """Add a user to a chat. Returns 1 on success."""

    __returning__ = int
    __api_method__ = "messages.addChatUser"

    chat_id: int
    user_id: int
    visible_messages_count: int = 0


class MessagesRemoveChatUser(VKMethod[int]):
    """Remove a user from a chat. Returns 1 on success."""

    __returning__ = int
    __api_method__ = "messages.removeChatUser"

    chat_id: int
    user_id: int
    member_id: int | None = None


class MessagesGetChatPreview(VKMethod[dict]):
    """Get chat preview by invite link."""

    __returning__ = dict
    __api_method__ = "messages.getChatPreview"

    link: str
    fields: str | None = None


class MessagesGetInviteLink(VKMethod[str]):
    """Get invite link for a chat."""

    __returning__ = str
    __api_method__ = "messages.getInviteLink"

    peer_id: int
    reset: int = 0
    group_id: int | None = None


class MessagesJoinChatByInviteLink(VKMethod[dict]):
    """Join a chat by invite link."""

    __returning__ = dict
    __api_method__ = "messages.joinChatByInviteLink"

    link: str


class MessagesDenyMessagesFromGroup(VKMethod[int]):
    """Disable messages from a community. Returns 1 on success."""

    __returning__ = int
    __api_method__ = "messages.denyMessagesFromGroup"

    group_id: int


class MessagesAllowMessagesFromGroup(VKMethod[int]):
    """Allow messages from a community. Returns 1 on success."""

    __returning__ = int
    __api_method__ = "messages.allowMessagesFromGroup"

    group_id: int
    key: str | None = None


class MessagesSetChatPhoto(VKMethod[dict]):
    """Set a chat photo from a previously uploaded image."""

    __returning__ = dict
    __api_method__ = "messages.setChatPhoto"

    file: str


class MessagesDeleteChatPhoto(VKMethod[dict]):
    """Delete chat photo."""

    __returning__ = dict
    __api_method__ = "messages.deleteChatPhoto"

    chat_id: int
    group_id: int | None = None


class MessagesSearchConversations(VKMethod[dict]):
    """Search conversations by query."""

    __returning__ = dict
    __api_method__ = "messages.searchConversations"

    q: str
    count: int = 20
    extended: int = 0
    fields: str | None = None
    group_id: int | None = None


class MessagesGetConversationMembers(VKMethod[dict]):
    """Get conversation members."""

    __returning__ = dict
    __api_method__ = "messages.getConversationMembers"

    peer_id: int
    fields: str | None = None
    group_id: int | None = None


class MessagesDeleteConversation(VKMethod[int]):
    """Delete a conversation. Returns the deleted message count."""

    __returning__ = int
    __api_method__ = "messages.deleteConversation"

    peer_id: int
    group_id: int | None = None


class MessagesRestore(VKMethod[int]):
    """Restore a deleted message. Returns 1 on success."""

    __returning__ = int
    __api_method__ = "messages.restore"

    message_id: int
    group_id: int | None = None


class MessagesGetByConversationMessageId(VKMethod[dict]):
    """Get messages by conversation message IDs."""

    __returning__ = dict
    __api_method__ = "messages.getByConversationMessageId"

    peer_id: int
    conversation_message_ids: list[int]
    extended: int = 0
    fields: str | None = None
    group_id: int | None = None


class MessagesGetLastActivity(VKMethod[dict]):
    """Get last activity for a user."""

    __returning__ = dict
    __api_method__ = "messages.getLastActivity"

    user_id: int


class MessagesGetHistoryAttachments(VKMethod[dict]):
    """Get attachments from chat history."""

    __returning__ = dict
    __api_method__ = "messages.getHistoryAttachments"

    peer_id: int
    media_type: str | None = None
    start_from: str | None = None
    count: int = 20
    photo_sizes: int = 0
    fields: str | None = None
    group_id: int | None = None


class MessagesGetImportantMessages(VKMethod[dict]):
    """Get important (bookmarked) messages."""

    __returning__ = dict
    __api_method__ = "messages.getImportantMessages"

    offset: int = 0
    count: int = 20
    extended: int = 0
    fields: str | None = None
    group_id: int | None = None


class MessagesMarkAsImportant(VKMethod[int]):
    """Mark messages as important (bookmark)."""

    __returning__ = int
    __api_method__ = "messages.markAsImportant"

    message_ids: int | str
    important: int = 1


class MessagesGetLongPollHistory(VKMethod[dict]):
    """Get Long Poll history for the current user."""

    __returning__ = dict
    __api_method__ = "messages.getLongPollHistory"

    ts: int
    pts: int | None = None
    preview_length: int = 0
    onlines: int = 0
    fields: str | None = None
    events_limit: int = 1000
    msgs_limit: int = 200
    max_msg_id: int | None = None
    group_id: int | None = None
    lp_version: int = 3


class MessagesGetPeersSubscriptions(VKMethod[dict]):
    """Get peer subscriptions."""

    __returning__ = dict
    __api_method__ = "messages.getPeersSubscriptions"

    peer_ids: list[int] | None = None
    group_id: int | None = None
