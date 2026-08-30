# Middleware

Middleware wraps every handler call. Use it for logging, rate limiting, auth checks, or injecting shared objects.

## How it works

```
Update → middleware_1 → middleware_2 → handler → middleware_2 → middleware_1
```

Each middleware calls `await call_next(event, data)` to pass control forward.

## Writing middleware

```python
from fastvk.middleware import BaseMiddleware
from fastvk.types import Message


class LoggingMiddleware(BaseMiddleware[Message]):
    async def __call__(self, call_next, event: Message, data: dict) -> None:
        print(f"[{event.peer_id}] {event.from_id}: {event.text}")
        await call_next(event, data)
        print(f"[{event.peer_id}] handler done")
```

## Registering middleware

Global (wraps every update, runs inside the automatic throttling middleware):

```python
bot = FastVK(token="...", group_id=123, middleware=[LoggingMiddleware()])
# or later:
bot.middleware(LoggingMiddleware())
```

Per-router (wraps only that router's handlers and its sub-routers):

```python
router = Router()
router.middleware(LoggingMiddleware())
```

## Injecting data into handlers

Anything a middleware puts into the `data` dict is injected into handlers
**by its type**:

```python
class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, pool) -> None:
        self.pool = pool

    async def __call__(self, call_next, event, data: dict) -> None:
        async with self.pool.acquire() as conn:
            data[Connection] = conn        # key by type…
            # data["db"] = conn            # …a plain key also works: it's
                                           #   registered under type(conn)
            return await call_next(event, data)


@bot.message()
async def handler(message: Message, conn: Connection) -> None:
    rows = await conn.fetch("SELECT 1")
```

The parameter is matched by its annotation, so annotate it with the value's
type (`conn: Connection`), not just a name.

## Built-in throttling

`FastVK` ships with a `ThrottlingMiddleware` that is **registered automatically** — no setup needed.
By default it allows 1 message per second per user. Extra messages are silently dropped.

```python
# default: 1 msg/s per user
bot = FastVK(token=TOKEN, group_id=GROUP_ID)

# custom rate
bot = FastVK(token=TOKEN, group_id=GROUP_ID, throttle_rate=0.5)

# disabled
bot = FastVK(token=TOKEN, group_id=GROUP_ID, throttle_rate=0)
```

See [ThrottlingMiddleware reference](../reference/fastvk.md#throttlingmiddleware) for details.
