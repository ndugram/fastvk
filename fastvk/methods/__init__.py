from .base import VKMethod
from .docs import DocsGetMessagesUploadServer, DocsSave
from .groups import GroupsGetById, GroupsGetLongPollServer, GroupsGetMembers
from .messages import (
    MessagesDelete,
    MessagesEdit,
    MessagesGetById,
    MessagesGetConversations,
    MessagesGetHistory,
    MessagesGetLongPollServer,
    MessagesMarkAsRead,
    MessagesPin,
    MessagesSend,
    MessagesSendEventAnswer,
    MessagesSetActivity,
    MessagesUnpin,
)
from .photos import PhotosGetMessagesUploadServer, PhotosSaveMessagesPhoto
from .users import UsersGet, UsersSearch
from .wall import WallGet, WallGetById, WallPost

# registry: VK method string → typed VKMethod class
# used by _APICallable to route dynamic calls through Pydantic
_REGISTRY: dict[str, type[VKMethod]] = {
    # messages
    "messages.send": MessagesSend,
    "messages.delete": MessagesDelete,
    "messages.edit": MessagesEdit,
    "messages.pin": MessagesPin,
    "messages.unpin": MessagesUnpin,
    "messages.markAsRead": MessagesMarkAsRead,
    "messages.getHistory": MessagesGetHistory,
    "messages.setActivity": MessagesSetActivity,
    "messages.getById": MessagesGetById,
    "messages.getConversations": MessagesGetConversations,
    "messages.sendMessageEventAnswer": MessagesSendEventAnswer,
    # users
    "users.get": UsersGet,
    "users.search": UsersSearch,
    # groups
    "groups.getLongPollServer": GroupsGetLongPollServer,
    "groups.getById": GroupsGetById,
    "groups.getMembers": GroupsGetMembers,
    # wall
    "wall.post": WallPost,
    "wall.get": WallGet,
    "wall.getById": WallGetById,
    # photos
    "photos.getMessagesUploadServer": PhotosGetMessagesUploadServer,
    "photos.saveMessagesPhoto": PhotosSaveMessagesPhoto,
    # docs
    "docs.getMessagesUploadServer": DocsGetMessagesUploadServer,
    "docs.save": DocsSave,
}

__all__ = [
    "VKMethod",
    "_REGISTRY",
    # messages
    "MessagesSend",
    "MessagesDelete",
    "MessagesEdit",
    "MessagesPin",
    "MessagesUnpin",
    "MessagesMarkAsRead",
    "MessagesGetHistory",
    "MessagesSetActivity",
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
    # wall
    "WallPost",
    "WallGet",
    "WallGetById",
    # photos
    "PhotosGetMessagesUploadServer",
    "PhotosSaveMessagesPhoto",
    # docs
    "DocsGetMessagesUploadServer",
    "DocsSave",
]
