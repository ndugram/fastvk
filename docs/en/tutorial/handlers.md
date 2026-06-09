# Handlers

Handlers are async functions registered with decorators. FastVK dispatches each incoming VK event to the first matching handler.

## `@bot.message()`

Fires on every incoming message (`message_new`).

```python
from fastvk import FastVK
from fastvk.types import Message

bot = FastVK(token="...", group_id=123)


@bot.message()
async def any_message(message: Message) -> None:
    await message.answer(f"You wrote: {message.text}")
```

Pass filters to narrow which messages trigger the handler:

```python
from fastvk import Command, F

@bot.message(Command("start"))
async def on_start(message: Message) -> None:
    await message.answer("Welcome!")

@bot.message(F.text == "hello")
async def on_hello(message: Message) -> None:
    await message.answer("Hello there!")
```

Multiple filters are combined with AND logic — all must pass:

```python
@bot.message(Command("ban"), F.from_id == ADMIN_ID)
async def ban_cmd(message: Message) -> None:
    ...
```

## `@bot.callback()`

Fires when a user presses an inline callback button (`message_event`).

```python
from fastvk.types import CallbackQuery
from fastvk.keyboard import Button, Keyboard

kb = Keyboard(inline=True).row(
    Button.callback("Click me", payload={"action": "ping"})
)


@bot.message(Command("start"))
async def send_kb(message: Message) -> None:
    await message.answer("Press the button:", keyboard=kb)


@bot.callback(F.payload == {"action": "ping"})
async def on_ping(callback: CallbackQuery) -> None:
    await callback.answer("Pong! 🏓")
```

## `@bot.on(event_type)`

Handles any VK event by raw type string.

```python
@bot.on("group_join")
async def on_join(message: Message) -> None:
    # update.object dict is injected if no typed handler matches
    ...

@bot.on("wall_post_new")
async def on_post(message: Message) -> None:
    ...
```

## Other group events

```python
@bot.message_reply()        # message_reply
async def on_reply(...): ...

@bot.message_allow()        # message_allow (newsletter opt-in)
async def on_allow(...): ...

@bot.group_join()           # group_join
async def on_join(...): ...

@bot.group_leave()          # group_leave
async def on_leave(...): ...

@bot.wall_post_new()        # wall_post_new
async def on_post(...): ...
```

## Dependency injection

Handler parameters are resolved automatically by type:

```python
from fastvk.types import Message, User
from fastvk.fsm import FSMContext
from fastvk.api.client import Bot

@bot.message()
async def handler(
    message: Message,   # the incoming message
    user: User,         # sender (fetched automatically)
    state: FSMContext,  # FSM context for this user
    bot: Bot,           # the Bot API client
) -> None:
    await message.answer(f"Hi {user.first_name}!")
```

You only declare what you need — unused params are simply not passed.

## Handler order

Handlers are checked in registration order. The **first** matching handler wins.

```python
@bot.message(Command("start"))      # checked first
async def start(...): ...

@bot.message()                      # fallback — catches everything else
async def fallback(...): ...
```
