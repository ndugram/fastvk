# Роутеры

Роутеры позволяют разделить хэндлеры по модулям и собрать их в одном боте.

## Зачем роутеры?

Один файл быстро разрастается. Раздели по фичам:

```
bot/
├── main.py
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   ├── catalog.py
│   └── admin.py
```

## Создание роутера

```python
# handlers/start.py
from fastvk import Router, CommandStart
from fastvk.types import Message

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Добро пожаловать!")
```

## Подключение роутеров

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

## Вложенные роутеры

Роутеры могут подключать другие роутеры:

```python
from fastvk import Router

admin_router = Router()
admin_router.include_router(admin_messages_router)
admin_router.include_router(admin_callbacks_router)

bot.include_router(admin_router)
```

## Фильтры на уровне роутера

Применить фильтр ко всем хэндлерам роутера:

```python
from fastvk import Router
from myfilters import IsAdmin

admin_router = Router()
admin_router.message.filter(IsAdmin())
admin_router.callback.filter(IsAdmin())


@admin_router.message()
async def admin_panel(message: Message) -> None:
    # выполняется только если IsAdmin() пройден
    await message.answer("Панель администратора")
```

## Полный пример

```python
# handlers/catalog.py
from fastvk import Router, F
from fastvk.types import Message, CallbackQuery
from fastvk.keyboard import Button, Keyboard

router = Router()

catalog_kb = (
    Keyboard(inline=True)
    .row(Button.callback("Товар 1", payload={"item": 1}),
         Button.callback("Товар 2", payload={"item": 2}))
)


@router.message(F.text == "Каталог")
async def catalog(message: Message) -> None:
    await message.answer("Выбери:", keyboard=catalog_kb)


@router.callback(F.payload["item"].exists())
async def item_selected(callback: CallbackQuery) -> None:
    item_id = callback.payload.get("item")
    await callback.answer(f"Выбран товар #{item_id}")
```
