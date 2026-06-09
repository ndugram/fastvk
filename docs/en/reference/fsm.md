# FSM

## State

```python
from fastvk.fsm import State, StatesGroup

class Form(StatesGroup):
    waiting_name = State()
    waiting_age  = State()

# String representation:
str(Form.waiting_name)  # "Form:waiting_name"
```

`State` objects can be compared with strings:

```python
current = await state.get_state()
if current == Form.waiting_name:
    ...
```

## FSMContext

Injected into handlers automatically. Key: `state: FSMContext`.

```python
async def handler(message: Message, state: FSMContext) -> None:
    ...
```

### Methods

```python
await state.get_state() -> str | None
await state.set_state(state: State | str | None) -> None

await state.get_data() -> dict
await state.set_data(data: dict) -> None
await state.update_data(**kwargs) -> None   # merge into existing

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

`key` is `(peer_id, user_id)`.

## MemoryStorage

```python
from fastvk.fsm import MemoryStorage

storage = MemoryStorage()
```

In-process dict storage. No persistence across restarts.

## RedisStorage

```python
from fastvk.fsm.redis import RedisStorage

# from URL (recommended)
storage = RedisStorage.from_url("redis://localhost:6379/0")
storage = RedisStorage.from_url("redis://localhost:6379/0", prefix="mybot")

# from existing Redis client
from redis.asyncio import Redis
storage = RedisStorage(Redis(...), prefix="fastvk")
```

Requires `pip install fastvk[redis]` (redis>=8.0.0).

Keys stored as:
- `{prefix}:state:{peer_id}:{user_id}`
- `{prefix}:data:{peer_id}:{user_id}` (JSON)

## SQLiteStorage

```python
from fastvk.fsm.sqlite import SQLiteStorage

# default path: "fastvk_fsm.db"
storage = SQLiteStorage("bot.db")

# custom table (useful when sharing a DB file between bots)
storage = SQLiteStorage("shared.db", table="mybot_fsm")
```

Requires `pip install fastvk[sqlite]` (aiosqlite>=0.20.0).

Table schema:
```sql
CREATE TABLE fastvk_fsm (
    peer_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    state   TEXT,
    data    TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY (peer_id, user_id)
)
```
