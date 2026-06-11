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

## Встроенный троттлинг

`FastVK` поставляется с `ThrottlingMiddleware`, который **регистрируется автоматически** — ничего настраивать не нужно.
По умолчанию пропускает 1 сообщение в секунду на пользователя. Лишние молча дропаются.

```python
# по умолчанию: 1 сообщение/с на пользователя
bot = FastVK(token=TOKEN, group_id=GROUP_ID)

# другой rate
bot = FastVK(token=TOKEN, group_id=GROUP_ID, throttle_rate=0.5)

# отключить
bot = FastVK(token=TOKEN, group_id=GROUP_ID, throttle_rate=0)
```

Подробнее: [справочник ThrottlingMiddleware](../reference/fastvk.md#throttlingmiddleware).
