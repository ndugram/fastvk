from __future__ import annotations

from .base import VKMethod


class DocsGetMessagesUploadServer(VKMethod[dict]):
    """
    Get upload server URL for sending a document in messages.

    ``type`` — ``"doc"``, ``"audio_message"``, or ``"graffiti"``.
    Returns dict with ``upload_url``. Upload your file via POST,
    then pass the response ``file`` field to :class:`DocsSave`.
    """

    __returning__ = dict
    __api_method__ = "docs.getMessagesUploadServer"

    peer_id: int
    type: str = "doc"


class DocsSave(VKMethod[dict]):
    """
    Save a document uploaded via :class:`DocsGetMessagesUploadServer`.

    Returns dict with ``type`` and the saved object (``doc`` or ``audio_message``).
    Build the attachment string: ``f"doc{doc['owner_id']}_{doc['id']}"``.
    """

    __returning__ = dict
    __api_method__ = "docs.save"

    file: str
    title: str | None = None
    tags: str | None = None
