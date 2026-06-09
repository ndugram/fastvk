from __future__ import annotations

from fastvk.enums.chat_action import ChatAction
from fastvk.enums.color import Color
from fastvk.enums.parse_mode import ParseMode


class TestParseMode:
    def test_html_value(self) -> None:
        assert ParseMode.HTML == "html"

    def test_markdown_value(self) -> None:
        assert ParseMode.MARKDOWN == "markdown"

    def test_value(self) -> None:
        assert ParseMode.HTML.value == "html"

    def test_equality_with_string(self) -> None:
        assert ParseMode.HTML == "html"
        assert ParseMode.MARKDOWN == "markdown"

    def test_is_str_subclass(self) -> None:
        assert isinstance(ParseMode.HTML, str)


class TestColor:
    def test_primary_value(self) -> None:
        assert Color.PRIMARY == "primary"

    def test_secondary_value(self) -> None:
        assert Color.SECONDARY == "secondary"

    def test_positive_value(self) -> None:
        assert Color.POSITIVE == "positive"

    def test_negative_value(self) -> None:
        assert Color.NEGATIVE == "negative"

    def test_equality_with_string(self) -> None:
        assert Color.PRIMARY == "primary"
        assert Color.NEGATIVE == "negative"

    def test_is_str_subclass(self) -> None:
        assert isinstance(Color.POSITIVE, str)


class TestChatAction:
    def test_typing_value(self) -> None:
        assert ChatAction.TYPING == "typing"

    def test_audio_message_value(self) -> None:
        assert ChatAction.AUDIO_MESSAGE == "audiomessage"

    def test_photo_value(self) -> None:
        assert ChatAction.PHOTO == "photo"

    def test_video_value(self) -> None:
        assert ChatAction.VIDEO == "video"

    def test_file_value(self) -> None:
        assert ChatAction.FILE == "file"

    def test_equality_with_string(self) -> None:
        assert ChatAction.TYPING == "typing"
        assert ChatAction.FILE == "file"

    def test_is_str_subclass(self) -> None:
        assert isinstance(ChatAction.TYPING, str)
