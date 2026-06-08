from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import State
    from .storage import BaseStorage


class FSMContext:
    """
    Per-user FSM state accessor injected into every handler.

    ```python
    @router.message(Command("start"))
    async def start(message: Message, state: FSMContext) -> None:
        await state.set_state(Form.waiting_name)
        await message.answer("Как тебя зовут?")

    @router.message(StateFilter(Form.waiting_name))
    async def got_name(message: Message, state: FSMContext) -> None:
        await state.update_data(name=message.text)
        await state.set_state(Form.waiting_age)
        await message.answer("Сколько тебе лет?")
    ```
    """

    def __init__(
        self,
        storage: BaseStorage,
        peer_id: int,
        user_id: int,
    ) -> None:
        self._storage = storage
        self._key = (peer_id, user_id)

    async def get_state(self) -> str | None:
        """Return the current state string, or ``None`` if no state is set."""
        return await self._storage.get_state(self._key)

    async def set_state(self, state: State | str | None) -> None:
        """
        Set the current state.

        Accepts a :class:`~fastvk.fsm.State` instance, a raw string,
        or ``None`` to clear the state without wiping data.
        """
        from .state import State as _State

        if isinstance(state, _State):
            state = state.state
        await self._storage.set_state(self._key, state)

    async def clear(self) -> None:
        """Reset both the state and the stored data for this user."""
        await self._storage.set_state(self._key, None)
        await self._storage.set_data(self._key, {})

    async def get_data(self) -> dict:
        """Return the stored data dict for this user."""
        return await self._storage.get_data(self._key)

    async def set_data(self, data: dict) -> None:
        """Replace the stored data dict for this user."""
        await self._storage.set_data(self._key, data)

    async def update_data(self, **kwargs: object) -> dict:
        """
        Merge *kwargs* into the stored data and return the updated dict.

        ```python
        await state.update_data(name="Alice", age=30)
        data = await state.get_data()  # {"name": "Alice", "age": 30}
        ```
        """
        data = await self.get_data()
        data.update(kwargs)
        await self.set_data(data)
        return data
