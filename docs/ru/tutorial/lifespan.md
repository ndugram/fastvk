# Lifespan

Lifespan позволяет выполнить код при запуске бота и при его остановке.

## Базовое использование

```python
from contextlib import asynccontextmanager
from fastvk import FastVK

@asynccontextmanager
async def lifespan(bot):
    # запуск
    print("Бот запускается...")
    yield
    # остановка
    print("Бот остановлен.")

bot = FastVK(token="...", group_id=123, lifespan=lifespan)
bot.run_polling()
```

Всё до `yield` выполняется один раз при запуске. Всё после — при остановке (включая Ctrl+C).

## Подключение к базе данных

```python
import asyncpg
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(bot):
    bot.db = await asyncpg.create_pool(dsn="postgresql://...")
    yield
    await bot.db.close()

bot = FastVK(token="...", group_id=123, lifespan=lifespan)
```

Затем используй `bot.db` в хэндлерах через DI:

```python
@bot.message()
async def handler(message: Message, bot: Bot) -> None:
    rows = await bot.db.fetch("SELECT * FROM users")
```

## HTTP клиент

```python
import aiohttp
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(bot):
    async with aiohttp.ClientSession() as session:
        bot.http = session
        yield
    # session закрывается автоматически
```

## Несколько ресурсов

```python
@asynccontextmanager
async def lifespan(bot):
    # открываем все ресурсы
    bot.db = await asyncpg.create_pool(dsn=DATABASE_URL)
    bot.redis = await aioredis.from_url(REDIS_URL)
    async with aiohttp.ClientSession() as session:
        bot.http = session
        yield
    # очистка в обратном порядке
    await bot.redis.close()
    await bot.db.close()
```

## skip_updates

Пропустить накопившиеся обновления пока бот был оффлайн:

```python
bot.run_polling(skip_updates=True)
```
