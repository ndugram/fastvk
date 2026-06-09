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

```python
bot = FastVK(token="...", group_id=123)

bot.message.middleware(LoggingMiddleware())
bot.callback.middleware(LoggingMiddleware())
```

Or on a router:

```python
router = Router()
router.message.middleware(LoggingMiddleware())
```

## Injecting data into handlers

Middleware can inject values into `data` dict, which feeds into handler DI:

```python
class DatabaseMiddleware(BaseMiddleware[Message]):
    def __init__(self, pool) -> None:
        self.pool = pool

    async def __call__(self, call_next, event: Message, data: dict) -> None:
        async with self.pool.acquire() as conn:
            data["db"] = conn          # injected into handler via DI
            await call_next(event, data)


@bot.message()
async def handler(message: Message, db) -> None:
    rows = await db.fetch("SELECT 1")
```

## Rate limiting example

```python
import time
from collections import defaultdict

class RateLimitMiddleware(BaseMiddleware[Message]):
    def __init__(self, limit: int = 5, window: int = 10) -> None:
        self._counts: dict[int, list[float]] = defaultdict(list)
        self._limit = limit
        self._window = window

    async def __call__(self, call_next, event: Message, data: dict) -> None:
        now = time.monotonic()
        user_id = event.from_id
        times = [t for t in self._counts[user_id] if now - t < self._window]
        self._counts[user_id] = times
        if len(times) >= self._limit:
            await event.answer("Too many requests. Slow down.")
            return
        self._counts[user_id].append(now)
        await call_next(event, data)
```
