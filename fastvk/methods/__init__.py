from .base import VKMethod
from .groups import GroupsGetById, GroupsGetLongPollServer, GroupsGetMembers
from .messages import (
    MessagesDelete,
    MessagesGetById,
    MessagesGetConversations,
    MessagesGetLongPollServer,
    MessagesSend,
    MessagesSendEventAnswer,
)
from .users import UsersGet, UsersSearch

# registry: VK method string → typed VKMethod class
# used by _APICallable to route dynamic calls through Pydantic
_REGISTRY: dict[str, type[VKMethod]] = {
    "messages.send": MessagesSend,
    "messages.delete": MessagesDelete,
    "messages.getById": MessagesGetById,
    "messages.getConversations": MessagesGetConversations,
    "messages.sendMessageEventAnswer": MessagesSendEventAnswer,
    "users.get": UsersGet,
    "users.search": UsersSearch,
    "groups.getLongPollServer": GroupsGetLongPollServer,
    "groups.getById": GroupsGetById,
    "groups.getMembers": GroupsGetMembers,
}

__all__ = [
    "VKMethod",
    "_REGISTRY",
    # messages
    "MessagesSend",
    "MessagesDelete",
    "MessagesGetById",
    "MessagesGetConversations",
    "MessagesGetLongPollServer",
    "MessagesSendEventAnswer",
    # users
    "UsersGet",
    "UsersSearch",
    # groups
    "GroupsGetById",
    "GroupsGetLongPollServer",
    "GroupsGetMembers",
]
