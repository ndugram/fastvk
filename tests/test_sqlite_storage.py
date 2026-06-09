from __future__ import annotations

import pytest

from fastvk.fsm.context import FSMContext
from fastvk.fsm.sqlite import SQLiteStorage
from fastvk.fsm.state import State, StatesGroup


@pytest.fixture
async def storage(tmp_path) -> SQLiteStorage:  # type: ignore[type-arg]
    s = SQLiteStorage(str(tmp_path / "test.db"))
    yield s
    await s.close()


class TestSQLiteStorage:
    async def test_get_state_empty(self, storage: SQLiteStorage) -> None:
        assert await storage.get_state((1, 2)) is None

    async def test_set_and_get_state(self, storage: SQLiteStorage) -> None:
        await storage.set_state((1, 2), "Form:step")
        assert await storage.get_state((1, 2)) == "Form:step"

    async def test_set_state_none_clears(self, storage: SQLiteStorage) -> None:
        await storage.set_state((1, 2), "Form:step")
        await storage.set_state((1, 2), None)
        assert await storage.get_state((1, 2)) is None

    async def test_get_data_empty(self, storage: SQLiteStorage) -> None:
        assert await storage.get_data((1, 2)) == {}

    async def test_set_and_get_data(self, storage: SQLiteStorage) -> None:
        await storage.set_data((1, 2), {"name": "Иван", "age": 30})
        data = await storage.get_data((1, 2))
        assert data == {"name": "Иван", "age": 30}

    async def test_set_data_replaces(self, storage: SQLiteStorage) -> None:
        await storage.set_data((1, 2), {"a": 1})
        await storage.set_data((1, 2), {"b": 2})
        assert await storage.get_data((1, 2)) == {"b": 2}

    async def test_different_keys_isolated(self, storage: SQLiteStorage) -> None:
        await storage.set_state((1, 10), "state_a")
        await storage.set_state((1, 20), "state_b")
        assert await storage.get_state((1, 10)) == "state_a"
        assert await storage.get_state((1, 20)) == "state_b"

    async def test_state_and_data_coexist(self, storage: SQLiteStorage) -> None:
        await storage.set_state((1, 1), "Form:step")
        await storage.set_data((1, 1), {"key": "value"})
        assert await storage.get_state((1, 1)) == "Form:step"
        assert await storage.get_data((1, 1)) == {"key": "value"}

    async def test_unicode_data(self, storage: SQLiteStorage) -> None:
        await storage.set_data((1, 1), {"city": "Москва", "emoji": "🤖"})
        assert await storage.get_data((1, 1)) == {"city": "Москва", "emoji": "🤖"}

    async def test_close_and_reopen(self, tmp_path) -> None:  # type: ignore[type-arg]
        path = str(tmp_path / "persist.db")
        s1 = SQLiteStorage(path)
        await s1.set_state((1, 1), "Form:step")
        await s1.set_data((1, 1), {"name": "Иван"})
        await s1.close()

        s2 = SQLiteStorage(path)
        assert await s2.get_state((1, 1)) == "Form:step"
        assert await s2.get_data((1, 1)) == {"name": "Иван"}
        await s2.close()

    async def test_close_twice_does_not_raise(self, storage: SQLiteStorage) -> None:
        await storage.close()
        await storage.close()

    async def test_custom_table_name(self, tmp_path) -> None:  # type: ignore[type-arg]
        s = SQLiteStorage(str(tmp_path / "custom.db"), table="my_fsm")
        await s.set_state((1, 1), "some_state")
        assert await s.get_state((1, 1)) == "some_state"
        await s.close()


class TestSQLiteFSMContext:
    async def test_full_flow(self, storage: SQLiteStorage) -> None:
        class Form(StatesGroup):
            waiting_name = State()
            waiting_age = State()

        ctx = FSMContext(storage, peer_id=1, user_id=1)

        await ctx.set_state(Form.waiting_name)
        assert await ctx.get_state() == "Form:waiting_name"

        await ctx.update_data(name="Иван")
        await ctx.set_state(Form.waiting_age)
        await ctx.update_data(age=25)

        data = await ctx.get_data()
        assert data["name"] == "Иван"
        assert data["age"] == 25
        assert await ctx.get_state() == "Form:waiting_age"

        await ctx.clear()
        assert await ctx.get_state() is None
        assert await ctx.get_data() == {}

    async def test_two_users_isolated(self, storage: SQLiteStorage) -> None:
        ctx_a = FSMContext(storage, peer_id=1, user_id=10)
        ctx_b = FSMContext(storage, peer_id=1, user_id=20)
        await ctx_a.set_state("state_a")
        await ctx_b.set_state("state_b")
        assert await ctx_a.get_state() == "state_a"
        assert await ctx_b.get_state() == "state_b"
