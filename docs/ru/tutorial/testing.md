# Тестирование

`fastvk.test` позволяет прогонять хэндлеры без токена и без сети.

```python
from fastvk.test import MockedBot, message_update, callback_update, dispatch
```

## MockedBot

Подкласс `Bot`, который записывает все вызовы API и возвращает заготовленные ответы.

```python
import pytest
from fastvk import Router
from fastvk.filters import Command
from fastvk.types import Message
from fastvk.test import MockedBot, dispatch, message_update

router = Router()


@router.message(Command("ping"))
async def ping(message: Message) -> None:
    await message.answer("pong")


@pytest.mark.asyncio
async def test_ping() -> None:
    bot = MockedBot()
    handled = await dispatch(router, bot, message_update("/ping"))

    assert handled is True
    assert bot.sent_messages[0]["message"] == "pong"
    bot.assert_called("messages.send")
```

### Заготовленные ответы

```python
bot = MockedBot()
bot.set_result("users.get", [{"id": 7, "first_name": "Ann", "last_name": "Lee"}])
bot.set_result("messages.send", 4242)
```

### Инспекция вызовов

| Атрибут / метод | Описание |
|---|---|
| `bot.calls` | Все записанные `Call(method, params)` по порядку |
| `bot.sent_messages` | `params` каждого вызова `messages.send` |
| `bot.assert_called("messages.send")` | Вернуть последний подходящий вызов или бросить исключение |
| `bot.assert_not_called("messages.edit")` | Бросить, если метод вызывался |

## Фабрики апдейтов

```python
message_update("/start", from_id=10, peer_id=2000000001)
message_update("photo", attachments=[{"type": "photo", "photo": {"owner_id": 1, "id": 2}}])
callback_update('{"action": "buy"}', user_id=10)
```

## dispatch()

```python
await dispatch(router, bot, update, storage=MemoryStorage(), data={MyDep: dep})
```

Возвращает `True`, если хэндлер сработал. `storage` и `data` необязательны —
значения из `data` внедряются в хэндлеры по типу, как это делал бы middleware.
