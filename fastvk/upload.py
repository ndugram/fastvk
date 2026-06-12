from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, Literal

import aiohttp

from .methods.docs import DocsGetMessagesUploadServer, DocsSave
from .methods.photos import PhotosGetMessagesUploadServer, PhotosSaveMessagesPhoto

if TYPE_CHECKING:
    from .api.client import Bot

UploadType = Literal["photo", "document", "audio_message", "graffiti"]


class Uploader:
    """
    High-level API for uploading media files to VK.

    Handles the full upload flow:
    1. Get upload server URL
    2. Upload file to the server
    3. Save the uploaded file via VK API

    ```python
    from fastvk import FastVK
    from fastvk.upload import Uploader

    bot = FastVK(token="vk1.a.YOUR_TOKEN")
    uploader = Uploader(bot.bot)

    # Upload photo
    attachment = await uploader.photo(peer_id=123456, file="image.jpg")
    await bot.bot.messages.send(peer_id=123456, message="Look!", attachment=attachment, random_id=0)

    # Upload document
    doc = await uploader.document(peer_id=123456, file="report.pdf", title="Monthly Report")

    # Upload audio message
    voice = await uploader.audio_message(peer_id=123456, file="voice.ogg")
    ```
    """

    def __init__(self, bot: Bot) -> None:
        """
        Initialize uploader with a :class:`~fastvk.Bot` instance.

        :param bot: Bot API client
        """
        self.bot = bot

    async def photo(
        self,
        peer_id: int,
        file: str | Path | BinaryIO,
        filename: str | None = None,
    ) -> str:
        """
        Upload a photo for sending in messages.

        :param peer_id: Destination peer ID (user or chat)
        :param file: Path to image file, or file-like object
        :param filename: Custom filename (required if ``file`` is a file-like object)
        :return: Attachment string like ``photo123456_789012``

        ```python
        # From file path
        attachment = await uploader.photo(peer_id=123, file="photo.jpg")

        # From bytes
        with open("photo.jpg", "rb") as f:
            attachment = await uploader.photo(peer_id=123, file=f, filename="photo.jpg")
        ```
        """

        server_data = await self.bot(PhotosGetMessagesUploadServer(peer_id=peer_id))
        upload_url = server_data["upload_url"]

        uploaded = await self._upload_file(upload_url, file, filename, field_name="photo")

        photos = await self.bot(
            PhotosSaveMessagesPhoto(
                photo=uploaded["photo"],
                server=uploaded["server"],
                hash=uploaded["hash"],
            )
        )

        if not photos:
            raise ValueError("Failed to save photo: empty response from VK")

        photo = photos[0]
        return f"photo{photo['owner_id']}_{photo['id']}"

    async def document(
        self,
        peer_id: int,
        file: str | Path | BinaryIO,
        filename: str | None = None,
        title: str | None = None,
        tags: str | None = None,
    ) -> str:
        """
        Upload a document for sending in messages.

        :param peer_id: Destination peer ID
        :param file: Path to file, or file-like object
        :param filename: Custom filename (required if ``file`` is a file-like object)
        :param title: Document title (visible to user). If not provided, uses filename.
        :param tags: Space-separated tags for search
        :return: Attachment string like ``doc123456_789012``

        ```python
        attachment = await uploader.document(
            peer_id=123,
            file="report.pdf",
            title="Monthly Report Q1"
        )
        ```
        """
        server_data = await self.bot(
            DocsGetMessagesUploadServer(peer_id=peer_id, type="doc")
        )
        upload_url = server_data["upload_url"]

        uploaded = await self._upload_file(upload_url, file, filename, field_name="file")

        result = await self.bot(
            DocsSave(
                file=uploaded["file"],
                title=title,
                tags=tags,
            )
        )

        doc_type = result.get("type", "doc")
        doc = result.get(doc_type)
        if not doc:
            raise ValueError(f"Failed to save document: unexpected response format {result}")

        return f"doc{doc['owner_id']}_{doc['id']}"

    async def audio_message(
        self,
        peer_id: int,
        file: str | Path | BinaryIO,
        filename: str | None = None,
    ) -> str:
        """
        Upload an audio message (voice message) for sending in messages.

        VK accepts OGG format with Opus codec. For best compatibility,
        ensure your audio file is encoded as OGG/Opus.

        :param peer_id: Destination peer ID
        :param file: Path to audio file (OGG/Opus recommended), or file-like object
        :param filename: Custom filename (required if ``file`` is a file-like object)
        :return: Attachment string like ``doc123456_789012``

        ```python
        voice = await uploader.audio_message(peer_id=123, file="voice.ogg")
        await bot.messages.send(peer_id=123, message="", attachment=voice, random_id=0)
        ```
        """
        server_data = await self.bot(
            DocsGetMessagesUploadServer(peer_id=peer_id, type="audio_message")
        )
        upload_url = server_data["upload_url"]

        uploaded = await self._upload_file(upload_url, file, filename, field_name="file")

        result = await self.bot(DocsSave(file=uploaded["file"]))

        audio_msg = result.get("audio_message")
        if not audio_msg:
            raise ValueError(f"Failed to save audio message: unexpected response {result}")

        return f"doc{audio_msg['owner_id']}_{audio_msg['id']}"

    async def graffiti(
        self,
        peer_id: int,
        file: str | Path | BinaryIO,
        filename: str | None = None,
    ) -> str:
        """
        Upload a graffiti (drawing) for sending in messages.

        :param peer_id: Destination peer ID
        :param file: Path to PNG file with transparent background, or file-like object
        :param filename: Custom filename (required if ``file`` is a file-like object)
        :return: Attachment string like ``doc123456_789012``

        ```python
        graffiti = await uploader.graffiti(peer_id=123, file="drawing.png")
        ```
        """
        server_data = await self.bot(
            DocsGetMessagesUploadServer(peer_id=peer_id, type="graffiti")
        )
        upload_url = server_data["upload_url"]

        uploaded = await self._upload_file(upload_url, file, filename, field_name="file")

        result = await self.bot(DocsSave(file=uploaded["file"]))

        graffiti_obj = result.get("graffiti")
        if not graffiti_obj:
            raise ValueError(f"Failed to save graffiti: unexpected response {result}")

        return f"doc{graffiti_obj['owner_id']}_{graffiti_obj['id']}"

    async def _upload_file(
        self,
        upload_url: str,
        file: str | Path | BinaryIO,
        filename: str | None,
        field_name: str,
    ) -> dict:
        """
        Upload a file to VK upload server.

        :param upload_url: Upload server URL from VK API
        :param file: File path or file-like object
        :param filename: Custom filename (required for file-like objects)
        :param field_name: Form field name (photo/file)
        :return: JSON response from upload server
        """
        session = await self.bot._get_session()

        # Determine if file is a path or file-like object
        if isinstance(file, (str, Path)):
            file_path = Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            actual_filename = filename or file_path.name
            mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

            with open(file_path, "rb") as f:
                file_data = f.read()
        else:
            # File-like object
            if filename is None:
                raise ValueError("filename is required when uploading from file-like object")

            actual_filename = filename
            mime_type = mimetypes.guess_type(actual_filename)[0] or "application/octet-stream"
            file_data = file.read()

        # Prepare multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field(
            field_name,
            file_data,
            filename=actual_filename,
            content_type=mime_type,
        )

        # Upload to VK server
        async with session.post(upload_url, data=form_data) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Upload failed with status {resp.status}: {await resp.text()}")
            return await resp.json()


__all__ = ["Uploader"]
