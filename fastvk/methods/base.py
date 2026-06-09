from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from ..api.client import Bot

T = TypeVar("T")


class VKMethod(BaseModel, Generic[T]):
    """
    Base class for all typed VK API methods.

    ```python
    from fastvk.methods import MessagesSend

    result = await bot(MessagesSend(peer_id=123, message="Привет!"))
    # or
    result = await MessagesSend(peer_id=123, message="Привет!").emit(bot)
    ```
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    if TYPE_CHECKING:
        __returning__: ClassVar[type]
        __api_method__: ClassVar[str]

    async def emit(self, bot: Bot) -> T:
        params = self.model_dump(exclude_none=True)
        return await bot._call(self.__api_method__, **params)  # type: ignore[return-value]
