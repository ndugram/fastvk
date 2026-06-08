from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class User:
    """
    VK user profile.

    Returned by ``api.users.get()`` and used in dependency injection.

    ```python
    async def get_user(message: Message, api: APIClient) -> User:
        result = await api.users.get(user_ids=message.from_id)
        data = result[0]
        return User(
            id=data["id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )
    ```
    """

    id: int
    """VK user ID."""

    first_name: str
    """User's first name."""

    last_name: str
    """User's last name."""

    @property
    def full_name(self) -> str:
        """Concatenated first and last name."""
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_dict(cls, data: dict) -> User:
        """Build a :class:`User` from a raw VK user dict."""
        return cls(
            id=data["id"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
        )
