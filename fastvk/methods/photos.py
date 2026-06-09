from __future__ import annotations

from .base import VKMethod


class PhotosGetMessagesUploadServer(VKMethod[dict]):
    """
    Get upload server URL for sending a photo in messages.

    Returns dict with ``upload_url``, ``album_id``, ``user_id``.
    Upload your file via POST to ``upload_url``, then pass the response
    fields to :class:`PhotosSaveMessagesPhoto`.
    """

    __returning__ = dict
    __api_method__ = "photos.getMessagesUploadServer"

    peer_id: int


class PhotosSaveMessagesPhoto(VKMethod[list]):
    """
    Save a photo uploaded via :class:`PhotosGetMessagesUploadServer`.

    Returns list of saved photo objects. Use ``photo[0]`` to build
    the attachment string: ``f"photo{photo['owner_id']}_{photo['id']}"``.
    """

    __returning__ = list
    __api_method__ = "photos.saveMessagesPhoto"

    photo: str
    server: int
    hash: str
