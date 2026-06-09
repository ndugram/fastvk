# Routers

Routers let you split handlers across multiple modules and compose them into one bot.

## Why routers?

A single file grows unmanageable fast. Split by feature:

```
bot/
├── main.py
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   ├── catalog.py
│   └── admin.py
```

## Creating a router

```python
# handlers/start.py
from fastvk import Router, CommandStart
from fastvk.types import Message

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Welcome!")
```

## Including routers

```python
# main.py
from fastvk import FastVK
from handlers.start import router as start_router
from handlers.catalog import router as catalog_router
from handlers.admin import router as admin_router

bot = FastVK(token="...", group_id=123)

bot.include_router(start_router)
bot.include_router(catalog_router)
bot.include_router(admin_router)

bot.run_polling()
```

## Nested routers

Routers can include other routers:

```python
from fastvk import Router

admin_router = Router()
admin_router.include_router(admin_messages_router)
admin_router.include_router(admin_callbacks_router)

bot.include_router(admin_router)
```

## Router-level filters

Apply a filter to every handler in a router:

```python
from fastvk import Router
from myfilters import IsAdmin

admin_router = Router()
admin_router.message.filter(IsAdmin())
admin_router.callback.filter(IsAdmin())


@admin_router.message()
async def admin_panel(message: Message) -> None:
    # only reached if IsAdmin() passes
    await message.answer("Admin panel")
```

## Full example

```python
# handlers/catalog.py
from fastvk import Router, F
from fastvk.types import Message, CallbackQuery
from fastvk.keyboard import Button, Keyboard

router = Router()

catalog_kb = (
    Keyboard(inline=True)
    .row(Button.callback("Item 1", payload={"item": 1}),
         Button.callback("Item 2", payload={"item": 2}))
)


@router.message(F.text == "Catalog")
async def catalog(message: Message) -> None:
    await message.answer("Choose:", keyboard=catalog_kb)


@router.callback(F.payload["item"].exists())
async def item_selected(callback: CallbackQuery) -> None:
    item_id = callback.payload.get("item")
    await callback.answer(f"Selected item #{item_id}")
```
