# Утилиты для тестов

```python
from fastvk.test import MockedBot, message_update, callback_update, dispatch
```

## MockedBot

Подкласс `Bot` без сети. Записывает вызовы, возвращает заготовленные ответы.

| Элемент | Описание |
|---|---|
| `MockedBot(token="test-token")` | Конструктор |
| `set_result(method: str, value)` | Задать возвращаемое значение метода VK (вызываемые значения выполняются) |
| `calls` | `list[Call]` — все вызовы по порядку; `Call.method`, `Call.params` |
| `sent_messages` | `list[dict]` — параметры каждого `messages.send` |
| `assert_called(method)` | Вернуть последний подходящий `Call`, иначе `AssertionError` |
| `assert_not_called(method)` | Бросить, если метод вызывался |

Ответы по умолчанию: `users.get` → один фейковый пользователь, `messages.send` /
`messages.edit` / `messages.sendMessageEventAnswer` → `1`.

## Фабрики апдейтов

```python
message_update(
    text="", *, from_id=1, peer_id=1, msg_id=1,
    attachments=None, payload=None, group_id=1, event_id=None,
) -> Update

callback_update(
    payload="{}", *, user_id=1, peer_id=1, cmid=1, group_id=1, event_id="evt-cb",
) -> Update
```

## dispatch

```python
async def dispatch(
    router: Router,
    bot: Bot,
    update: Update,
    *,
    storage: BaseStorage | None = None,   # по умолчанию: новый MemoryStorage
    data: dict | None = None,             # внедряется в хэндлеры по типу
) -> bool
```

Прогоняет `update` через `router` и возвращает, сработал ли хэндлер.
