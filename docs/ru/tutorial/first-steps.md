# Первые шаги

## Установка

```console
$ pip install fastvk
```

## Получение токена

1. Зайди в настройки группы ВКонтакте → **Работа с API**.
2. Создай ключ доступа с правами на **сообщения**.
3. Во вкладке **Long Poll API** включи Long Poll и выбери события: `Входящее сообщение`, `Нажатие на кнопку`.

## Минимальный бот

```python
from fastvk import FastVK
from fastvk.types import Message

bot = FastVK(token="vk1.a....", group_id=123456789)


@bot.message()
async def echo(message: Message) -> None:
    await message.answer(message.text)


bot.run_polling()
```

`FastVK` наследует `Router`, поэтому все декораторы (`@bot.message()`, `@bot.callback()`) доступны прямо на объекте бота.

## Запуск

```console
$ python main.py
15:00:00  INFO      fastvk  FastVK started (group_id=123456789)
```

Останови через `Ctrl+C`.

## Параметры FastVK

```python
from fastvk import FastVK
from fastvk.fsm import MemoryStorage

bot = FastVK(
    token="vk1.a....",        # токен группы (обязательно)
    group_id=123456789,       # ID группы (обязательно)
    storage=MemoryStorage(),  # хранилище FSM
    dashboard=True,           # веб-дашборд на http://127.0.0.1:8080
    dashboard_host="0.0.0.0",
    dashboard_port=8080,
)
```

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `token` | `str` | — | Токен доступа группы |
| `group_id` | `int` | — | ID группы ВКонтакте |
| `storage` | `BaseStorage` | `MemoryStorage()` | Хранилище FSM |
| `middleware` | `BaseMiddleware` | `None` | Middleware (один или список) |
| `lifespan` | `Callable` | `None` | Async context manager для startup/shutdown |
| `dashboard` | `bool` | `False` | Включить веб-дашборд |
| `dashboard_host` | `str` | `"127.0.0.1"` | Хост дашборда |
| `dashboard_port` | `int` | `8080` | Порт дашборда |

## Структура проекта

Для небольших ботов достаточно одного файла. Для средних и крупных:

```
my_bot/
├── main.py          # FastVK + run_polling
├── handlers/
│   ├── __init__.py
│   ├── start.py     # /start, /help
│   ├── catalog.py
│   └── admin.py
└── states.py        # StatesGroup классы
```

```python
# main.py
from fastvk import FastVK
from handlers.start import router as start_router
from handlers.catalog import router as catalog_router

bot = FastVK(token="...", group_id=123)
bot.include_router(start_router)
bot.include_router(catalog_router)
bot.run_polling()
```

Подробнее в разделе [Роутеры](routers.md).
