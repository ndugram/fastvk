# Middleware

Middleware оборачивает каждый вызов хэндлера. Используй для логирования, rate limiting, проверки прав или внедрения общих объектов.

## Как работает

```
Update → middleware_1 → middleware_2 → handler → middleware_2 → middleware_1
```

Каждый middleware вызывает `await call_next(event, data)` чтобы передать управление дальше.

## Написание middleware

```python
from fastvk.middleware import BaseMiddleware
from fastvk.types import Message


class LoggingMiddleware(BaseMiddleware[Message]):
    async def __call__(self, call_next, event: Message, data: dict) -> None:
        print(f"[{event.peer_id}] {event.from_id}: {event.text}")
        await call_next(event, data)
        print(f"[{event.peer_id}] хэндлер завершён")
```

## Регистрация middleware

```python
bot = FastVK(token="...", group_id=123)

bot.message.middleware(LoggingMiddleware())
bot.callback.middleware(LoggingMiddleware())
```

Или на роутере:

```python
router = Router()
router.message.middleware(LoggingMiddleware())
```

## Внедрение данных в хэндлеры

Middleware может добавлять значения в словарь `data`, который используется DI хэндлера:

```python
class DatabaseMiddleware(BaseMiddleware[Message]):
    def __init__(self, pool) -> None:
        self.pool = pool

    async def __call__(self, call_next, event: Message, data: dict) -> None:
        async with self.pool.acquire() as conn:
            data["db"] = conn          # внедряется в хэндлер через DI
            await call_next(event, data)


@bot.message()
async def handler(message: Message, db) -> None:
    rows = await db.fetch("SELECT 1")
```

## Пример rate limiting

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
            await event.answer("Слишком много запросов. Подожди.")
            return
        self._counts[user_id].append(now)
        await call_next(event, data)
```
