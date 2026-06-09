from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Update(BaseModel):
    type: str
    object: dict[str, Any]
    group_id: int
    event_id: str
