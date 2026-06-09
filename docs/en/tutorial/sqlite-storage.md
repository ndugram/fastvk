# SQLiteStorage

`SQLiteStorage` persists FSM state to a local SQLite file. No external services required — the database is a single `.db` file on disk.

## Installation

```bash
pip install fastvk[sqlite]
# or
pip install aiosqlite
```

## Basic usage

```python
from fastvk import FastVK
from fastvk.fsm.sqlite import SQLiteStorage

bot = FastVK(
    token="...",
    group_id=123,
    storage=SQLiteStorage("bot.db"),
)
```

State and data survive bot restarts. A table named `fastvk_fsm` is created automatically on first run.

## Custom table name

Useful when multiple bots share the same database file:

```python
storage = SQLiteStorage("shared.db", table="mybot_fsm")
```

## Comparison of storages

| Storage | Persistence | External service | Install |
|---|---|---|---|
| `MemoryStorage` | ✗ (lost on restart) | — | built-in |
| `SQLiteStorage` | ✓ | — | `pip install aiosqlite` |
| `RedisStorage` | ✓ | Redis server | `pip install fastvk[redis]` |

## Full example

```python
import os
from fastvk import FastVK
from fastvk.filters import Command, StateFilter
from fastvk.fsm import FSMContext, State, StatesGroup
from fastvk.fsm.sqlite import SQLiteStorage
from fastvk.types import Message

bot = FastVK(
    token=os.environ["VK_TOKEN"],
    group_id=int(os.environ["VK_GROUP_ID"]),
    storage=SQLiteStorage("bot.db"),
)


class Form(StatesGroup):
    waiting_name = State()
    waiting_age  = State()


@bot.message(Command("start"))
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.waiting_name)
    await message.answer("What's your name?")


@bot.message(StateFilter(Form.waiting_name))
async def got_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.waiting_age)
    await message.answer("How old are you?")


@bot.message(StateFilter(Form.waiting_age))
async def got_age(message: Message, state: FSMContext) -> None:
    data = await state.update_data(age=message.text)
    await state.clear()
    await message.answer(f"Name: {data['name']}, age: {data['age']} — saved!")


bot.run_polling()
```
