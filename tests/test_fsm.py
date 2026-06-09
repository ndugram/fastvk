from __future__ import annotations


from fastvk.fsm.context import FSMContext
from fastvk.fsm.state import State, StatesGroup
from fastvk.fsm.storage import MemoryStorage


class TestState:
    def test_state_name_set_by_descriptor(self) -> None:
        class Form(StatesGroup):
            waiting_name = State()

        assert Form.waiting_name.state == "Form:waiting_name"

    def test_multiple_states_in_group(self) -> None:
        class MyForm(StatesGroup):
            first = State()
            second = State()
            third = State()

        assert MyForm.first.state == "MyForm:first"
        assert MyForm.second.state == "MyForm:second"
        assert MyForm.third.state == "MyForm:third"

    def test_state_equality(self) -> None:
        class Form(StatesGroup):
            step = State()

        assert Form.step == Form.step

    def test_state_inequality(self) -> None:
        class Form(StatesGroup):
            a = State()
            b = State()

        assert Form.a != Form.b

    def test_state_repr(self) -> None:
        class Form(StatesGroup):
            step = State()

        assert "Form:step" in repr(Form.step)

    def test_manual_state_name(self) -> None:
        s = State("custom_name")
        assert s.state == "custom_name"


class TestMemoryStorage:
    async def test_get_state_empty(self) -> None:
        storage = MemoryStorage()
        state = await storage.get_state((1, 2))
        assert state is None

    async def test_set_and_get_state(self) -> None:
        storage = MemoryStorage()
        await storage.set_state((1, 2), "Form:step")
        assert await storage.get_state((1, 2)) == "Form:step"

    async def test_get_data_empty(self) -> None:
        storage = MemoryStorage()
        data = await storage.get_data((1, 2))
        assert data == {}

    async def test_set_and_get_data(self) -> None:
        storage = MemoryStorage()
        await storage.set_data((1, 2), {"name": "Иван", "age": 30})
        data = await storage.get_data((1, 2))
        assert data == {"name": "Иван", "age": 30}

    async def test_different_keys_isolated(self) -> None:
        storage = MemoryStorage()
        await storage.set_state((1, 10), "state_a")
        await storage.set_state((1, 20), "state_b")

        assert await storage.get_state((1, 10)) == "state_a"
        assert await storage.get_state((1, 20)) == "state_b"

    async def test_close_does_not_raise(self) -> None:
        storage = MemoryStorage()
        await storage.set_state((1, 2), "some_state")
        await storage.close()


class TestFSMContext:
    async def test_set_state_with_string(self, storage: MemoryStorage) -> None:
        ctx = FSMContext(storage, peer_id=1, user_id=1)
        await ctx.set_state("Form:step")
        assert await ctx.get_state() == "Form:step"

    async def test_set_state_with_state_object(self, storage: MemoryStorage) -> None:
        class Form(StatesGroup):
            step = State()

        ctx = FSMContext(storage, peer_id=1, user_id=1)
        await ctx.set_state(Form.step)
        assert await ctx.get_state() == "Form:step"

    async def test_set_state_none_clears_state(self, storage: MemoryStorage) -> None:
        ctx = FSMContext(storage, peer_id=1, user_id=1)
        await ctx.set_state("Form:step")
        await ctx.set_state(None)
        assert await ctx.get_state() is None

    async def test_update_data_merges(self, storage: MemoryStorage) -> None:
        ctx = FSMContext(storage, peer_id=1, user_id=1)
        await ctx.update_data(name="Иван")
        await ctx.update_data(age=30)
        data = await ctx.get_data()
        assert data == {"name": "Иван", "age": 30}

    async def test_update_data_returns_merged(self, storage: MemoryStorage) -> None:
        ctx = FSMContext(storage, peer_id=1, user_id=1)
        result = await ctx.update_data(key="value")
        assert result == {"key": "value"}

    async def test_clear_resets_state_and_data(self, storage: MemoryStorage) -> None:
        ctx = FSMContext(storage, peer_id=1, user_id=1)
        await ctx.set_state("Form:step")
        await ctx.update_data(name="Иван")
        await ctx.clear()
        assert await ctx.get_state() is None
        assert await ctx.get_data() == {}

    async def test_different_users_isolated(self, storage: MemoryStorage) -> None:
        ctx_a = FSMContext(storage, peer_id=1, user_id=10)
        ctx_b = FSMContext(storage, peer_id=1, user_id=20)
        await ctx_a.set_state("state_a")
        await ctx_b.set_state("state_b")
        assert await ctx_a.get_state() == "state_a"
        assert await ctx_b.get_state() == "state_b"

    async def test_set_data_replaces(self, storage: MemoryStorage) -> None:
        ctx = FSMContext(storage, peer_id=1, user_id=1)
        await ctx.update_data(old_key="old")
        await ctx.set_data({"new_key": "new"})
        data = await ctx.get_data()
        assert data == {"new_key": "new"}
        assert "old_key" not in data
