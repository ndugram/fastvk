# FastVK

**FastVK** — асинхронный фреймворк для VK-ботов на Python, вдохновлённый FastAPI и aiogram.

[Начать →](tutorial/first-steps.md){ .md-button .md-button--primary }
[Туториал](tutorial/index.md){ .md-button }

---

## Ключевые возможности

- **Декораторный API** — `@bot.message()`, `@bot.callback()`, `@bot.on("event")`.
- **Фильтры** — `Command`, `CommandStart`, `Text`, `F.text == "..."`, `StateFilter`, `regexp`.
- **FSM** — `StatesGroup`, `FSMContext`, `MemoryStorage` / `RedisStorage`.
- **DI** — параметры хэндлера (`message: Message`, `state: FSMContext`, `user: User`) резолвятся автоматически по типу.
- **Typed методы** — `MessagesSend`, `MessagesEdit`, `WallPost` и другие с полной поддержкой IDE.
- **Роутеры** — `Router` для разбивки бота по файлам.
- **Middleware** — перехват любого события до хэндлера.
- **Dashboard** — встроенный веб-дашборд со статистикой.

## Установка

```console
$ pip install fastvk
```

## Быстрый пример

```python
from fastvk import FastVK, CommandStart
from fastvk.types import Message

bot = FastVK(token="vk1.a....", group_id=123456789)


@bot.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f"Привет, {message.from_user.first_name}!")


bot.run_polling()
```
