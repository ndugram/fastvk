# FSM

## State

```python
from fastvk.fsm import State, StatesGroup

class Form(StatesGroup):
    waiting_name = State()
    waiting_age  = State()

# Строковое представление:
str(Form.waiting_name)  # "Form:waiting_name"
```

Объекты `State` можно сравнивать со строками:

```python
current = await state.get_state()
if current == Form.waiting_name:
    ...
```

## FSMContext

Внедряется в хэндлеры автоматически. Ключ: `state: FSMContext`.

```python
async def handler(message: Message, state: FSMContext) -> None:
    ...
```

### Методы

```python
await state.get_state() -> str | None
await state.set_state(state: State | str | None) -> None

await state.get_data() -> dict
await state.set_data(data: dict) -> None
await state.update_data(**kwargs) -> None   # слияние с существующими

await state.clear() -> None   # state=None, data={}
```

## BaseStorage

```python
class BaseStorage(ABC):
    async def get_state(self, key: tuple[int, int]) -> str | None: ...
    async def set_state(self, key: tuple[int, int], state: str | None) -> None: ...
    async def get_data(self, key: tuple[int, int]) -> dict: ...
    async def set_data(self, key: tuple[int, int], data: dict) -> None: ...
    async def close(self) -> None: ...
```

`key` — это `(peer_id, user_id)`.

## MemoryStorage

```python
from fastvk.fsm import MemoryStorage

storage = MemoryStorage()
```

Хранилище в виде словаря в памяти. Нет сохранения между перезапусками.

## RedisStorage

```python
from fastvk.fsm.redis import RedisStorage

# из URL (рекомендуется)
storage = RedisStorage.from_url("redis://localhost:6379/0")
storage = RedisStorage.from_url("redis://localhost:6379/0", prefix="mybot")

# из существующего Redis клиента
from redis.asyncio import Redis
storage = RedisStorage(Redis(...), prefix="fastvk")
```

Требует `pip install fastvk[redis]` (redis>=8.0.0).

Ключи хранятся как:
- `{prefix}:state:{peer_id}:{user_id}`
- `{prefix}:data:{peer_id}:{user_id}` (JSON)

## SQLiteStorage

```python
from fastvk.fsm.sqlite import SQLiteStorage

# путь по умолчанию: "fastvk_fsm.db"
storage = SQLiteStorage("bot.db")

# кастомное имя таблицы (если несколько ботов делят один файл БД)
storage = SQLiteStorage("shared.db", table="mybot_fsm")
```

Требует `pip install fastvk[sqlite]` (aiosqlite>=0.20.0).

Схема таблицы:
```sql
CREATE TABLE fastvk_fsm (
    peer_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    state   TEXT,
    data    TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY (peer_id, user_id)
)
```
