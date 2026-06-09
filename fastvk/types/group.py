from __future__ import annotations

from pydantic import BaseModel


class Group(BaseModel):
    """VK community info returned by ``bot.get_me()``."""

    id: int
    name: str
    screen_name: str
    type: str = ""
    photo_50: str = ""
    photo_100: str = ""
    photo_200: str = ""
    description: str = ""
    members_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> Group:
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            screen_name=data.get("screen_name", ""),
            type=data.get("type", ""),
            photo_50=data.get("photo_50", ""),
            photo_100=data.get("photo_100", ""),
            photo_200=data.get("photo_200", ""),
            description=data.get("description", ""),
            members_count=data.get("members_count", 0),
        )

    @property
    def mention(self) -> str:
        return f"@{self.screen_name}"

    @property
    def url(self) -> str:
        return f"https://vk.com/{self.screen_name}"
