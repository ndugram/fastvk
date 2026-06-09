# First steps

## Installation

```console
$ pip install fastvk
```

## Getting a token

1. Go to your VK group settings → **API usage**.
2. Create an access key with **messages** permission.
3. In the **Long Poll API** tab, enable Long Poll and select events: `Incoming message`, `Button press`.

## Minimal bot

```python
from fastvk import FastVK
from fastvk.types import Message

bot = FastVK(token="vk1.a....", group_id=123456789)


@bot.message()
async def echo(message: Message) -> None:
    await message.answer(message.text)


bot.run_polling()
```

`FastVK` extends `Router`, so all decorators (`@bot.message()`, `@bot.callback()`) are available directly on the bot object.

## Running

```console
$ python main.py
15:00:00  INFO      fastvk  FastVK started (group_id=123456789)
```

Stop with `Ctrl+C`.

## FastVK parameters

```python
from fastvk import FastVK
from fastvk.fsm import MemoryStorage

bot = FastVK(
    token="vk1.a....",        # group token (required)
    group_id=123456789,       # group ID (required)
    storage=MemoryStorage(),  # FSM storage
    dashboard=True,           # web dashboard at http://127.0.0.1:8080
    dashboard_host="0.0.0.0",
    dashboard_port=8080,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `token` | `str` | — | Group access token |
| `group_id` | `int` | — | VK group ID |
| `storage` | `BaseStorage` | `MemoryStorage()` | FSM storage backend |
| `middleware` | `BaseMiddleware` | `None` | Middleware (single or list) |
| `lifespan` | `Callable` | `None` | Async context manager for startup/shutdown |
| `dashboard` | `bool` | `False` | Enable web dashboard |
| `dashboard_host` | `str` | `"127.0.0.1"` | Dashboard host |
| `dashboard_port` | `int` | `8080` | Dashboard port |

## Project structure

For small bots one file is fine. For larger projects:

```
my_bot/
├── main.py          # FastVK + run_polling
├── handlers/
│   ├── __init__.py
│   ├── start.py     # /start, /help
│   ├── catalog.py
│   └── admin.py
└── states.py        # StatesGroup classes
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

See [Routers](routers.md) for details.
