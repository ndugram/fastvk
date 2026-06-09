# SQLiteStorage

`SQLiteStorage` сохраняет FSM-состояния в локальный файл SQLite. Никаких внешних сервисов — только один `.db`-файл на диске.

## Установка

```bash
pip install fastvk[sqlite]
# или
pip install aiosqlite
```

## Базовое использование

```python
from fastvk import FastVK
from fastvk.fsm.sqlite import SQLiteStorage

bot = FastVK(
    token="...",
    group_id=123,
    storage=SQLiteStorage("bot.db"),
)
```

Состояния и данные сохраняются между перезапусками. Таблица `fastvk_fsm` создаётся автоматически при первом запуске.

## Кастомное имя таблицы

Полезно, если несколько ботов используют один файл базы данных:

```python
storage = SQLiteStorage("shared.db", table="mybot_fsm")
```

## Сравнение хранилищ

| Хранилище | Сохранение данных | Внешний сервис | Установка |
|---|---|---|---|
| `MemoryStorage` | ✗ (теряется при перезапуске) | — | встроено |
| `SQLiteStorage` | ✓ | — | `pip install aiosqlite` |
| `RedisStorage` | ✓ | Redis сервер | `pip install fastvk[redis]` |

## Полный пример

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
    await message.answer("Как тебя зовут?")


@bot.message(StateFilter(Form.waiting_name))
async def got_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.waiting_age)
    await message.answer("Сколько тебе лет?")


@bot.message(StateFilter(Form.waiting_age))
async def got_age(message: Message, state: FSMContext) -> None:
    data = await state.update_data(age=message.text)
    await state.clear()
    await message.answer(f"Имя: {data['name']}, возраст: {data['age']} — сохранено!")


bot.run_polling()
```
