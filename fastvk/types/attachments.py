from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class _Attachment(BaseModel):
    """Base for typed message attachments."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: str = ""
    owner_id: int = 0
    id: int = 0
    access_key: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @property
    def attachment_string(self) -> str:
        """VK attachment string, e.g. ``photo-1_2`` or ``photo-1_2_abcdef``."""
        base = f"{self.type}{self.owner_id}_{self.id}"
        return f"{base}_{self.access_key}" if self.access_key else base

    def __str__(self) -> str:
        return self.attachment_string


class PhotoSize(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str = ""
    url: str = ""
    width: int = 0
    height: int = 0


class Photo(_Attachment):
    type: str = "photo"
    album_id: int = 0
    text: str = ""
    date: int = 0
    sizes: list[PhotoSize] = Field(default_factory=list)

    @property
    def largest(self) -> PhotoSize | None:
        """The highest-resolution size available."""
        if not self.sizes:
            return None
        return max(self.sizes, key=lambda s: s.width * s.height)

    @property
    def url(self) -> str:
        """URL of the largest size (empty string if unknown)."""
        largest = self.largest
        return largest.url if largest else ""


class Video(_Attachment):
    type: str = "video"
    title: str = ""
    description: str = ""
    duration: int = 0
    date: int = 0


class Audio(_Attachment):
    type: str = "audio"
    artist: str = ""
    title: str = ""
    duration: int = 0
    url: str = ""


class Document(_Attachment):
    type: str = "doc"
    title: str = ""
    size: int = 0
    ext: str = ""
    url: str = ""


class AudioMessage(_Attachment):
    type: str = "audio_message"
    duration: int = 0
    link_ogg: str = ""
    link_mp3: str = ""
    transcript: str = ""
    waveform: list[int] = Field(default_factory=list)


class Sticker(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str = "sticker"
    sticker_id: int = 0
    product_id: int = 0
    raw: dict[str, Any] = Field(default_factory=dict)


class Graffiti(_Attachment):
    type: str = "graffiti"
    url: str = ""
    width: int = 0
    height: int = 0


class Link(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str = "link"
    url: str = ""
    title: str = ""
    description: str = ""
    caption: str = ""
    raw: dict[str, Any] = Field(default_factory=dict)


class Poll(_Attachment):
    type: str = "poll"
    question: str = ""
    votes: int = 0
    anonymous: bool = False
    multiple: bool = False


class WallPost(_Attachment):
    type: str = "wall"
    from_id: int = 0
    to_id: int = 0
    text: str = ""
    date: int = 0


_TYPE_MAP: dict[str, type[BaseModel]] = {
    "photo": Photo,
    "video": Video,
    "audio": Audio,
    "doc": Document,
    "audio_message": AudioMessage,
    "sticker": Sticker,
    "graffiti": Graffiti,
    "link": Link,
    "poll": Poll,
    "wall": WallPost,
}


def parse_attachment(item: dict[str, Any]) -> Any:
    """Turn one raw VK attachment dict into a typed model (or ``dict`` if unknown)."""
    a_type = item.get("type", "")
    body = item.get(a_type, {})
    model = _TYPE_MAP.get(a_type)
    if model is None:
        return item
    payload = dict(body)
    payload.setdefault("type", a_type)
    payload["raw"] = body
    try:
        return model.model_validate(payload)
    except Exception:
        return item


def parse_attachments(items: list[dict[str, Any]]) -> list[Any]:
    return [parse_attachment(i) for i in items]


__all__ = [
    "Photo",
    "PhotoSize",
    "Video",
    "Audio",
    "Document",
    "AudioMessage",
    "Sticker",
    "Graffiti",
    "Link",
    "Poll",
    "WallPost",
    "parse_attachment",
    "parse_attachments",
]
