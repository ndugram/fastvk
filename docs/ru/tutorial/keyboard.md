# Клавиатура

FastVK предоставляет классы `Button` и `Keyboard` для создания VK клавиатур.

## Типы кнопок

```python
from fastvk.keyboard import Button
from fastvk.enums import Color

# Текстовая кнопка (обычная клавиатура)
Button.text("Нажми меня")
Button.text("Да",  color=Color.POSITIVE)
Button.text("Нет", color=Color.NEGATIVE)
Button.text("Назад", color=Color.PRIMARY, payload={"cmd": "back"})

# Callback кнопка (inline клавиатура — вызывает message_event)
Button.callback("Лайк 👍", payload={"vote": 1})
Button.callback("Дизлайк 👎", payload={"vote": 0})

# Кнопка-ссылка
Button.link("GitHub", url="https://github.com")

# Кнопка геолокации
Button.location()
```

### Цвета кнопок

| Цвет | Значение | Применение |
|---|---|---|
| `Color.PRIMARY` | `"primary"` | Синий — основное действие |
| `Color.SECONDARY` | `"secondary"` | Белый — дополнительное |
| `Color.POSITIVE` | `"positive"` | Зелёный — подтверждение |
| `Color.NEGATIVE` | `"negative"` | Красный — отмена/опасность |

## Создание клавиатуры

```python
from fastvk.keyboard import Keyboard

# Обычная клавиатура с рядами
kb = (
    Keyboard(one_time=True)
    .row(Button.text("✅ Да",  color=Color.POSITIVE),
         Button.text("❌ Нет", color=Color.NEGATIVE))
    .row(Button.text("Отмена"))
)

await message.answer("Выбери:", keyboard=kb)
```

```python
# Inline клавиатура
kb = (
    Keyboard(inline=True)
    .row(Button.callback("👍", payload={"v": 1}),
         Button.callback("👎", payload={"v": 0}))
)

await message.answer("Оцени:", keyboard=kb)
```

### Параметры Keyboard

| Параметр | По умолчанию | Описание |
|---|---|---|
| `one_time` | `False` | Скрыть клавиатуру после нажатия |
| `inline` | `False` | Inline клавиатура (прикреплена к сообщению) |

### Методы

```python
kb.row(*buttons)    # добавить новый ряд кнопок
kb.add(*buttons)    # добавить кнопки в последний ряд
kb.build()          # сериализовать в JSON строку
str(kb)             # то же что build()
Keyboard.remove()   # JSON строка для удаления клавиатуры
```

## Удалить клавиатуру

```python
await message.answer("Клавиатура убрана", keyboard=Keyboard.remove())
```

## Полный пример

```python
from fastvk import FastVK, CommandStart, F
from fastvk.keyboard import Button, Keyboard
from fastvk.types import Message, CallbackQuery
from fastvk.enums import Color

bot = FastVK(token="...", group_id=123)

menu_kb = (
    Keyboard(inline=True)
    .row(
        Button.callback("🛒 Каталог",    payload={"action": "catalog"}),
        Button.callback("📦 Мои заказы", payload={"action": "orders"}),
    )
    .row(Button.callback("📞 Поддержка", payload={"action": "support"}))
)


@bot.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Главное меню:", keyboard=menu_kb)


@bot.callback(F.payload.action == "catalog")
async def on_catalog(callback: CallbackQuery) -> None:
    await callback.answer("Открываю каталог...")


@bot.callback(F.payload.action == "orders")
async def on_orders(callback: CallbackQuery) -> None:
    await callback.answer("У тебя пока нет заказов")


bot.run_polling()
```
