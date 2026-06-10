from __future__ import annotations

from pydantic import BaseModel


class CommandArgs(BaseModel):
    model_config = {"frozen": True}

    command: str
    args: tuple[str, ...]
    text: str

    def __getitem__(self, index: int) -> str:
        return self.args[index]

    def __len__(self) -> int:
        return len(self.args)

    def __bool__(self) -> bool:
        return bool(self.args)

    def get(self, index: int, default: str = "") -> str:
        try:
            return self.args[index]
        except IndexError:
            return default
