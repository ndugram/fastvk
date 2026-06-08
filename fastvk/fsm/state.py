from __future__ import annotations


class State:
    """
    A single FSM state.

    Declare as a class attribute of a :class:`StatesGroup` subclass —
    the state name is set automatically from the class and attribute names.

    ```python
    class Form(StatesGroup):
        waiting_name = State()   # state == "Form:waiting_name"
        waiting_age  = State()   # state == "Form:waiting_age"
    ```
    """

    def __init__(self, state: str | None = None) -> None:
        self._state = state

    def __set_name__(self, owner: type, name: str) -> None:
        if self._state is None:
            self._state = f"{owner.__name__}:{name}"

    @property
    def state(self) -> str | None:
        """Fully qualified state name, e.g. ``"Form:waiting_name"``."""
        return self._state

    def __repr__(self) -> str:
        return f"<State {self._state!r}>"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, State):
            return self._state == other._state
        if isinstance(other, str):
            return self._state == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._state)


class _StatesGroupMeta(type):
    """Metaclass that auto-assigns state names to all :class:`State` attributes."""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict,
    ) -> _StatesGroupMeta:
        states: dict[str, State] = {}
        for attr_name, attr_val in namespace.items():
            if isinstance(attr_val, State) and attr_val._state is None:
                attr_val._state = f"{name}:{attr_name}"
                states[attr_name] = attr_val
        namespace["_states"] = states
        return super().__new__(mcs, name, bases, namespace)


class StatesGroup(metaclass=_StatesGroupMeta):
    """
    Base class for grouping related FSM states.

    ```python
    class RegistrationForm(StatesGroup):
        waiting_name  = State()
        waiting_age   = State()
        waiting_email = State()
    ```
    """

    _states: dict[str, State]
