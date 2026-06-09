<p align="center">
  <img src="logo.svg" width="480">
</p>
<p align="center">
    <em>Async VK bot framework with FastAPI-style decorators and aiogram-style FSM.</em>
</p>
<p align="center">
<a href="https://github.com/ndugram/fastvk/actions/workflows/tests.yml" target="_blank">
    <img src="https://github.com/ndugram/fastvk/actions/workflows/tests.yml/badge.svg" alt="Tests">
</a>
<a href="https://pypi.org/project/fastvk" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastvk?color=%234C75A3&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/fastvk" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/fastvk.svg?color=%234C75A3" alt="Supported Python versions">
</a>
<a href="https://pypi.org/project/fastvk" target="_blank">
    <img src="https://img.shields.io/pypi/dm/fastvk?color=%234C75A3&label=downloads" alt="Monthly downloads">
</a>
<a href="https://pepy.tech/projects/fastvk" target="_blank">
    <img src="https://img.shields.io/pepy/dt/fastvk?color=%234C75A3&label=total%20downloads" alt="Total downloads">
</a>
<a href="https://github.com/ndugram/fastvk" target="_blank">
    <img src="https://img.shields.io/github/stars/ndugram/fastvk?style=social" alt="GitHub Stars">
</a>
</p>

---

**Source Code**: <a href="https://github.com/ndugram/fastvk" target="_blank">https://github.com/ndugram/fastvk</a>

---

FastVK — это современный **асинхронный фреймворк для VK-ботов** на Python. Вдохновлён FastAPI и aiogram — декораторы для хэндлеров, DI через аннотации типов, FSM, middleware и typed VK API методы.

Ключевые особенности:

- **Декораторный API** — `@bot.message()`, `@bot.callback()`, `@bot.on("event")`.
- **Фильтры** — `Command`, `Text`, `F.text == "..."`, `StateFilter`, `regexp`.
- **FSM** — состояния через `StatesGroup`, `FSMContext`, хранилища `MemoryStorage` / `RedisStorage`.
- **DI** — параметры хэндлера (`message: Message`, `state: FSMContext`, `user: User`) подставляются автоматически.
- **Typed методы** — `MessagesSend`, `MessagesEdit`, `WallPost` и другие с полной поддержкой IDE.
- **Роутеры** — `Router` для разбивки бота по файлам, как в FastAPI.
- **Middleware** — перехват любого события до хэндлера.
- **Dashboard** — встроенный веб-дашборд со статистикой.

## Требования

Python 3.10+

FastVK использует:

- [`aiohttp`](https://docs.aiohttp.org/) — async HTTP клиент для VK API и Long Poll.
- [`pydantic`](https://docs.pydantic.dev/) — типизация всех VK объектов.

## Установка

```console
$ pip install fastvk

---> 100%
```

Для Redis FSM хранилища:

```console
$ pip install fastvk[redis]
```

## Пример

```python
from fastvk import FastVK, CommandStart, Command
from fastvk.types import Message
from fastvk.fsm import FSMContext, State, StatesGroup
from fastvk.filters import StateFilter, Text

bot = FastVK(token="vk1.a....", group_id=123456)


class Form(StatesGroup):
    waiting_name = State()


@bot.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.waiting_name)
    await message.answer("Привет! Как тебя зовут?")


@bot.message(StateFilter(Form.waiting_name))
async def got_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.clear()
    await message.answer(f"Отлично, {message.text}! 👋")


@bot.message(Command("help"))
async def help_cmd(message: Message) -> None:
    await message.answer("Доступные команды: /start, /help")


bot.run_polling()
```

<details markdown="1">
<summary>Пример с клавиатурой и callback</summary>

```python
from fastvk import FastVK, F
from fastvk.keyboard import Button, Keyboard
from fastvk.types import Message, CallbackQuery

bot = FastVK(token="vk1.a....", group_id=123456)

vote_kb = (
    Keyboard(inline=True)
    .row(
        Button.callback("👍 Нравится", payload={"vote": "like"}),
        Button.callback("👎 Не нравится", payload={"vote": "dislike"}),
    )
)


@bot.message(F.text == "голосовать")
async def send_vote(message: Message) -> None:
    await message.answer("Оцени:", keyboard=vote_kb)


@bot.callback(F.payload == {"vote": "like"})
async def on_like(callback: CallbackQuery) -> None:
    await callback.answer("Спасибо за лайк! ❤️")


@bot.callback(F.payload == {"vote": "dislike"})
async def on_dislike(callback: CallbackQuery) -> None:
    await callback.answer("Жаль... Мы станем лучше!")


bot.run_polling()
```
</details>
