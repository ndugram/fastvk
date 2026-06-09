from enum import Enum


class ParseMode(str, Enum):
    """Text formatting mode for messages."""

    HTML = "html"
    MARKDOWN = "markdown"
