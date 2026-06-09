<p align="center">
  <img src="docs/logo.svg" width="480">
</p>
<p align="center">
    <em>Async VK bot framework with FastAPI-style decorators and aiogram-style FSM.</em>
</p>
<p align="center">
<a href="https://pypi.org/project/fastvk" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastvk?color=%234C75A3&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/fastvk" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/fastvk.svg?color=%234C75A3" alt="Supported Python versions">
</a>
<a href="https://github.com/ndugram/fastvk" target="_blank">
    <img src="https://img.shields.io/github/stars/ndugram/fastvk?style=social" alt="GitHub Stars">
</a>
<a href="https://github.com/ndugram/fastvk/blob/master/LICENSE" target="_blank">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
</a>
</p>

---

**Source Code**: <a href="https://github.com/ndugram/fastvk" target="_blank">https://github.com/ndugram/fastvk</a>

---

FastVK is a modern **async VK bot framework** for Python. It brings a decorator-based handler API — similar to FastAPI and aiogram, but for VK — with FSM, middleware, filters, and clean dependency injection out of the box.

Key features:

- **Familiar** — if you know FastAPI or aiogram, you already know FastVK. Same patterns, same ergonomics.
- **Async** — built on <a href="https://docs.aiohttp.org/" target="_blank">aiohttp</a> with full async/await support from top to bottom.
- **FSM** — built-in Finite State Machine with `State`, `StatesGroup`, and pluggable storage backends.
- **Filters** — `Command`, `Text`, `StateFilter`, `FromUser`, `IsChat` and custom filters via any callable.
- **Injection** — handler parameters injected by name: `message`, `state`, `api`, `update` — no manual wiring.
- **Routers** — split handlers across multiple `Router` instances, include them into the main bot.
- **Middleware** — intercept every update before and after handlers with `BaseMiddleware`.
- **Typed** — full type annotations throughout; works great with mypy and pyright.

## Requirements

Python 3.10+

FastVK depends on:

- <a href="https://docs.aiohttp.org/" target="_blank"><code>aiohttp</code></a> — async HTTP transport for Long Poll and VK API calls.
- <a href="https://github.com/annotated-doc/annotated-doc" target="_blank"><code>annotated-doc</code></a> — `Doc()` annotations for rich parameter documentation.

## Installation

```console
$ pip install fastvk

---> 100%
```

## Example

### Create it

Create a file `main.py`:

```python
from fastvk import FastVK
from fastvk.filters import Command
from fastvk.types import Message

bot = FastVK(token="vk1.a.YOUR_TOKEN", group_id=123456789)


@bot.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer("Привет! Я FastVK бот 🤖")


if __name__ == "__main__":
    bot.run_polling()
```

### Run it

```console
$ python main.py
```

### Check it

You will see output like:

```
INFO  fastvk  FastVK started (group_id=123456789)
INFO  fastvk  Polling started
```

Send `/start` to your bot — it replies instantly.

### Upgrade the example

<details markdown="1">
<summary>With FSM (multi-step forms)...</summary>

Use `StatesGroup` and `State` to collect data across multiple messages:

```python
from fastvk import FastVK
from fastvk.filters import Command, StateFilter
from fastvk.fsm import FSMContext, State, StatesGroup
from fastvk.types import Message

bot = FastVK(token="vk1.a.YOUR_TOKEN", group_id=123456789)


class RegistrationForm(StatesGroup):
    waiting_name = State()
    waiting_age  = State()


@bot.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationForm.waiting_name)
    await message.answer("Как тебя зовут?")


@bot.message(StateFilter(RegistrationForm.waiting_name))
async def got_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(RegistrationForm.waiting_age)
    await message.answer(f"Отлично, {message.text}! Сколько тебе лет?")


@bot.message(StateFilter(RegistrationForm.waiting_age))
async def got_age(message: Message, state: FSMContext) -> None:
    data = await state.update_data(age=message.text)
    await state.clear()
    await message.answer(
        f"Готово!\nИмя: {data['name']}\nВозраст: {data['age']}"
    )


if __name__ == "__main__":
    bot.run_polling()
```

</details>

<details markdown="1">
<summary>With routers...</summary>

Split handlers into separate modules and include them into the bot:

```python
from fastvk import FastVK, Router
from fastvk.filters import Command, Text
from fastvk.types import Message

shop_router = Router()


@shop_router.message(Command("catalog"))
async def catalog(message: Message) -> None:
    await message.answer("📦 Наш каталог: ...")


@shop_router.message(Text("цена", contains=True, ignore_case=True))
async def price_mention(message: Message) -> None:
    await message.answer("Цены начинаются от 99₽")


bot = FastVK(token="vk1.a.YOUR_TOKEN", group_id=123456789)
bot.include_router(shop_router)

if __name__ == "__main__":
    bot.run_polling()
```

</details>

<details markdown="1">
<summary>With middleware...</summary>

Intercept every incoming update to add logging, rate limiting, or custom data:

```python
from collections.abc import Awaitable, Callable
from typing import Any

from fastvk import FastVK
from fastvk.middleware import BaseMiddleware
from fastvk.filters import Command
from fastvk.types import Message


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        print(f"→ incoming: {type(event).__name__}")
        result = await handler(event, data)
        print(f"← handled")
        return result


bot = FastVK(
    token="vk1.a.YOUR_TOKEN",
    group_id=123456789,
    middleware=[LoggingMiddleware()],
)


@bot.message(Command("ping"))
async def ping(message: Message) -> None:
    await message.answer("pong")


if __name__ == "__main__":
    bot.run_polling()
```

</details>

<details markdown="1">
<summary>With filters...</summary>

Combine built-in and custom filters on any handler:

```python
from fastvk import FastVK
from fastvk.filters import Command, FromUser, IsChat, Text
from fastvk.types import Message

ADMIN_ID = 123456789

bot = FastVK(token="vk1.a.YOUR_TOKEN", group_id=987654321)


@bot.message(Command("ban"), FromUser(ADMIN_ID))
async def admin_ban(message: Message) -> None:
    await message.answer("Пользователь заблокирован.")


@bot.message(IsChat("private"), Text("помощь", contains=True, ignore_case=True))
async def help_in_pm(message: Message) -> None:
    await message.answer("Список команд: /start, /help")


def is_long_message(message: Message, data: dict) -> bool:
    return len(message.text or "") > 200


@bot.message(is_long_message)
async def long_message(message: Message) -> None:
    await message.answer("Это очень длинное сообщение!")


if __name__ == "__main__":
    bot.run_polling()
```

</details>

<details markdown="1">
<summary>With raw VK API calls...</summary>

Access the full VK API via the injected `api` parameter:

```python
from fastvk import FastVK
from fastvk import Bot
from fastvk.filters import Command
from fastvk.types import Message

bot = FastVK(token="vk1.a.YOUR_TOKEN", group_id=123456789)


@bot.message(Command("me"))
async def cmd_me(message: Message, bot: Bot) -> None:
    users = await bot.users.get(user_ids=message.from_id, fields="photo_200")
    name = f"{users[0]['first_name']} {users[0]['last_name']}"
    await message.answer(f"Ты: {name}")


@bot.message(Command("members"))
async def cmd_members(message: Message, bot: Bot) -> None:
    data = await bot.groups.getMembers(group_id=app.group_id, count=1)
    await message.answer(f"Участников в группе: {data['count']}")


if __name__ == "__main__":
    bot.run_polling()
```

</details>

<details markdown="1">
<summary>With event handlers...</summary>

Handle any VK event type — not just messages:

```python
from fastvk import FastVK
from fastvk import Bot
from fastvk.types import Update

bot = FastVK(token="vk1.a.YOUR_TOKEN", group_id=123456789)


@bot.group_join()
async def on_join(event: dict, bot: Bot) -> None:
    user_id = event.get("user_id")
    await api.messages.send(
        peer_id=user_id,
        message="Добро пожаловать в группу!",
        random_id=0,
    )


@bot.wall_post_new()
async def on_new_post(event: dict) -> None:
    print(f"Новый пост: {event.get('id')}")


@bot.on("photo_new")
async def on_photo(update: Update) -> None:
    print(f"Новое фото: {update.object}")


if __name__ == "__main__":
    bot.run_polling()
```

</details>

## Dependency injection

Handler parameters are injected **by type** — declare what you need, framework provides it. No manual wiring:

| Type | What you get |
|---|---|
| `Message` | Parsed incoming message (for `message_new` events) |
| `FSMContext` | FSM context for current user |
| `Bot` | VK Bot API client |
| `Update` | Full raw update object |

```python
@router.message()
async def handler(
    message: Message,
    state: FSMContext,
    bot: Bot,
) -> None:
    ...
```

## Contributing

Contributions are welcome! Please open an issue before submitting a pull request.

Found a bug? Open an issue on <a href="https://github.com/ndugram/fastvk/issues" target="_blank">GitHub</a>.

## License

This project is licensed under the terms of the <a href="https://github.com/ndugram/fastvk/blob/master/LICENSE" target="_blank">MIT license</a>.
