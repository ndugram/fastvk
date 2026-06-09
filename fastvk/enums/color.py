from enum import Enum


class Color(str, Enum):
    """Keyboard button colors."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    POSITIVE = "positive"
    NEGATIVE = "negative"
