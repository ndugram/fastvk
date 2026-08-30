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

# Открыть VK Mini App
Button.vkapps("Открыть приложение", app_id=1234567, hash="ref=menu")

# Кнопка VK Pay
Button.vkpay(action="pay-to-group", group_id=123, amount=100, description="Донат")
Button.vkpay(action="transfer-to-group", group_id=123, aid=1)
Button.vkpay(action="transfer-to-user", user_id=456, aid=1)
```

### Кнопка VK Pay

`Button.vkpay` собирает внутренний `hash` из именованных параметров — вручную строить строку не нужно.

```python
# Оплата в группу (самый частый случай)
Button.vkpay(
    action="pay-to-group",
    group_id=123456,
    amount=100,           # рублей
    description="Донат",
)

# Перевод в группу
Button.vkpay(action="transfer-to-group", group_id=123456, aid=1)

# Перевод пользователю
Button.vkpay(action="transfer-to-user", user_id=654321, aid=1)
```

| Параметр | Нужен для | Описание |
|---|---|---|
| `action` | все | `"pay-to-group"` / `"transfer-to-group"` / `"transfer-to-user"` |
| `group_id` | групповые действия | ID целевой группы |
| `user_id` | `transfer-to-user` | ID пользователя |
| `amount` | `pay-to-group` | Сумма в рублях |
| `description` | `pay-to-group` | Описание платежа |
| `merchant_id` | опционально | Идентификатор мерчанта |
| `aid` | переводы | Дополнительный ID |

!!! note
    Кнопки VK Pay работают только на **inline** клавиатурах (`Keyboard(inline=True)`).

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

## Карусель

Карусель — горизонтально прокручиваемый набор карточек, отправляемый через
параметр сообщения `template` (только inline, до 10 карточек).

```python
from fastvk import Carousel, Button

carousel = (
    Carousel()
    .element(
        title="Товар 1",
        description="99 ₽",
        photo_id="-1_2",                                    # id вложения-фото
        buttons=[Button.callback("Купить", payload={"buy": 1})],
        link="https://example.com/1",                        # действие по тапу на карточку
    )
    .element(title="Товар 2", buttons=[Button.callback("Купить", payload={"buy": 2})])
)

await message.answer_carousel(carousel, text="Каталог")
# или: await bot.messages.send(peer_id=..., template=str(carousel), random_id=0)
```

| Параметр `element()` | Описание |
|---|---|
| `title` / `description` | Тексты карточки |
| `photo_id` | id вложения-фото (`{owner}_{id}`) |
| `buttons` | Список `Button.*` (callback / link) |
| `link` | Действие по тапу на всю карточку (`open_link`); без него — `open_photo` |

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
