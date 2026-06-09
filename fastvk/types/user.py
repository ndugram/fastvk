from __future__ import annotations

from pydantic import BaseModel


class User(BaseModel):
    id: int
    first_name: str
    last_name: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_dict(cls, data: dict) -> User:
        return cls(
            id=data["id"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
        )
