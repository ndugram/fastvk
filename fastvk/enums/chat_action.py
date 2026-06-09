from enum import Enum


class ChatAction(str, Enum):
    """Status shown in chat while bot is processing (messages.setActivity)."""

    TYPING = "typing"
    AUDIO_MESSAGE = "audiomessage"
    PHOTO = "photo"
    VIDEO = "video"
    FILE = "file"
