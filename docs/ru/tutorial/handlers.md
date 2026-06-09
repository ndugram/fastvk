# Хэндлеры

Хэндлеры — это async функции, зарегистрированные через декораторы. FastVK отправляет каждое входящее VK событие в первый подходящий хэндлер.

## `@bot.message()`

Срабатывает на каждое входящее сообщение (`message_new`).

```python
from fastvk import FastVK
from fastvk.types import Message

bot = FastVK(token="...", group_id=123)


@bot.message()
async def any_message(message: Message) -> None:
    await message.answer(f"Ты написал: {message.text}")
```

Передай фильтры, чтобы хэндлер срабатывал только на нужные сообщения:

```python
from fastvk import Command, F

@bot.message(Command("start"))
async def on_start(message: Message) -> None:
    await message.answer("Привет!")

@bot.message(F.text == "привет")
async def on_hello(message: Message) -> None:
    await message.answer("И тебе привет!")
```

Несколько фильтров объединяются по AND — все должны пройти:

```python
@bot.message(Command("ban"), F.from_id == ADMIN_ID)
async def ban_cmd(message: Message) -> None:
    ...
```

## `@bot.callback()`

Срабатывает когда пользователь нажимает inline callback кнопку (`message_event`).

```python
from fastvk.types import CallbackQuery
from fastvk.keyboard import Button, Keyboard

kb = Keyboard(inline=True).row(
    Button.callback("Нажми меня", payload={"action": "ping"})
)


@bot.message(Command("start"))
async def send_kb(message: Message) -> None:
    await message.answer("Нажми кнопку:", keyboard=kb)


@bot.callback(F.payload == {"action": "ping"})
async def on_ping(callback: CallbackQuery) -> None:
    await callback.answer("Понг! 🏓")
```

## `@bot.on(event_type)`

Обрабатывает любое VK событие по строке типа.

```python
@bot.on("group_join")
async def on_join() -> None:
    ...

@bot.on("wall_post_new")
async def on_post() -> None:
    ...
```

## Другие события группы

```python
@bot.message_reply()        # message_reply
async def on_reply(...): ...

@bot.message_allow()        # message_allow (подписка на рассылку)
async def on_allow(...): ...

@bot.group_join()           # group_join
async def on_join(...): ...

@bot.group_leave()          # group_leave
async def on_leave(...): ...

@bot.wall_post_new()        # wall_post_new
async def on_post(...): ...
```

## Dependency injection

Параметры хэндлера резолвятся автоматически по типу:

```python
from fastvk.types import Message, User
from fastvk.fsm import FSMContext
from fastvk.api.client import Bot

@bot.message()
async def handler(
    message: Message,   # входящее сообщение
    user: User,         # отправитель (подгружается автоматически)
    state: FSMContext,  # FSM контекст для этого пользователя
    bot: Bot,           # клиент VK API
) -> None:
    await message.answer(f"Привет, {user.first_name}!")
```

Объявляй только то, что нужно — лишние параметры просто не передаются.

## Порядок хэндлеров

Хэндлеры проверяются в порядке регистрации. Побеждает **первый** подходящий.

```python
@bot.message(Command("start"))      # проверяется первым
async def start(...): ...

@bot.message()                      # fallback — ловит всё остальное
async def fallback(...): ...
```
