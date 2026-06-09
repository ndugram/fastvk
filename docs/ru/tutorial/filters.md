# Фильтры

Фильтры определяют, должен ли хэндлер обработать входящее событие. Передаются аргументами в `@bot.message()` и другие декораторы.

## Command

Совпадает с сообщениями, начинающимися с команды бота.

```python
from fastvk import Command

@bot.message(Command("start"))
async def on_start(message: Message) -> None:
    await message.answer("Привет!")

# несколько команд в одном хэндлере
@bot.message(Command("help", "faq", "info"))
async def on_help(message: Message) -> None:
    await message.answer("Текст помощи")
```

Обрабатывает все формы: `/start`, `/start@mybot`, `/start аргумент`.

### Кастомный префикс

```python
# срабатывает на !ban и /ban
@bot.message(Command("ban", "kick", prefix="!/"))
async def mod_cmd(message: Message) -> None:
    ...
```

`prefix` — строка, каждый символ которой является допустимым префиксом.

## CommandStart / CommandHelp

Шорткаты для самых распространённых команд:

```python
from fastvk import CommandStart, CommandHelp

@bot.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Привет!")

@bot.message(CommandHelp())
async def help_cmd(message: Message) -> None:
    await message.answer("Вот что я умею...")
```

## Text

Совпадает с текстом сообщения точно или по подстроке.

```python
from fastvk.filters import Text

@bot.message(Text("привет"))
async def on_hello(message: Message) -> None:
    await message.answer("И тебе привет!")

# чувствительно к регистру
@bot.message(Text("ПРИВЕТ", ignore_case=False))
async def case_sensitive(message: Message) -> None: ...

# поиск подстроки
@bot.message(Text("скидка", contains=True, ignore_case=True))
async def on_promo(message: Message) -> None:
    await message.answer("Вот твой промокод!")

# несколько значений
@bot.message(Text("да", "ладно", "окей"))
async def on_yes(message: Message) -> None: ...
```

| Параметр | По умолчанию | Описание |
|---|---|---|
| `*texts` | — | Значения для сравнения |
| `contains` | `False` | Поиск подстроки вместо точного совпадения |
| `ignore_case` | `True` | Без учёта регистра |

## F — магический фильтр

`F` строит ленивые выражения на основе атрибутов с полной поддержкой IDE.

```python
from fastvk import F

# равенство
@bot.message(F.text == "привет")
async def on_hello(message: Message) -> None: ...

# неравенство
@bot.message(F.text != "")
async def non_empty(message: Message) -> None: ...

# подстрока
@bot.message(F.text.contains("скидка"))
async def on_deal(message: Message) -> None: ...

# startswith / endswith
@bot.message(F.text.startswith("/"))
async def any_command(message: Message) -> None: ...

# in_ — одно из значений
@bot.message(F.from_id.in_(111, 222, 333))
async def admins_only(message: Message) -> None: ...

# regexp
@bot.message(F.text.regexp(r"^\d+$"))
async def digits_only(message: Message) -> None:
    await message.answer(f"Получил число: {message.text}")

# вложенные атрибуты (для CallbackQuery)
@bot.callback(F.payload == {"action": "buy"})
async def on_buy(callback: CallbackQuery) -> None: ...

@bot.callback(F.payload.action == "buy")
async def on_buy2(callback: CallbackQuery) -> None: ...
```

### Комбинирование фильтров: `&`, `|`, `~`

```python
# AND
@bot.message(F.text.contains("купить") & F.from_id.in_(VIP_IDS))
async def vip_buy(message: Message) -> None: ...

# OR
@bot.message(F.text.contains("акция") | F.text.contains("скидка"))
async def on_promo(message: Message) -> None: ...

# NOT
@bot.message(~F.text.startswith("/"))
async def not_command(message: Message) -> None: ...
```

## StateFilter

Срабатывает только когда пользователь находится в определённом FSM состоянии. Подробнее в разделе [FSM](fsm.md).

```python
from fastvk.filters import StateFilter
from fastvk.fsm import State, StatesGroup


class Form(StatesGroup):
    waiting_name = State()
    waiting_age = State()


@bot.message(StateFilter(Form.waiting_name))
async def got_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.waiting_age)
    await message.answer("Сколько тебе лет?")
```

## FromUser / IsChat

```python
from fastvk.filters import FromUser, IsChat

# только от конкретного пользователя
@bot.message(FromUser(123456))
async def from_vip(message: Message) -> None: ...

# только в групповых чатах (peer_id > 2_000_000_000)
@bot.message(IsChat())
async def chat_only(message: Message) -> None: ...
```
