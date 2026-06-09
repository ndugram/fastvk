# FastVK

**FastVK** is an async VK bot framework for Python, inspired by FastAPI and aiogram.

[Get started →](tutorial/first-steps.md){ .md-button .md-button--primary }
[Tutorial](tutorial/index.md){ .md-button }

---

## Key features

- **Decorator API** — `@bot.message()`, `@bot.callback()`, `@bot.on("event")`.
- **Filters** — `Command`, `CommandStart`, `Text`, `F.text == "..."`, `StateFilter`, `regexp`.
- **FSM** — `StatesGroup`, `FSMContext`, `MemoryStorage` / `RedisStorage`.
- **DI** — handler params (`message: Message`, `state: FSMContext`, `user: User`) resolved automatically by type.
- **Typed methods** — `MessagesSend`, `MessagesEdit`, `WallPost` and more with full IDE support.
- **Routers** — `Router` for splitting handlers across files.
- **Middleware** — intercept any event before it reaches a handler.
- **Dashboard** — built-in web dashboard with live stats.

## Installation

```console
$ pip install fastvk
```

## Quick example

```python
from fastvk import FastVK, CommandStart
from fastvk.types import Message

bot = FastVK(token="vk1.a....", group_id=123456789)


@bot.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f"Hello, {message.from_user.first_name}!")


bot.run_polling()
```
