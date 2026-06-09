# Lifespan

Lifespan lets you run setup code before polling starts and teardown code after it stops.

## Basic usage

```python
from contextlib import asynccontextmanager
from fastvk import FastVK

@asynccontextmanager
async def lifespan(bot):
    # startup
    print("Bot starting...")
    yield
    # shutdown
    print("Bot stopped.")

bot = FastVK(token="...", group_id=123, lifespan=lifespan)
bot.run_polling()
```

Everything before `yield` runs once on startup. Everything after runs on shutdown (including Ctrl+C).

## Database connection

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

Then use `bot.db` in handlers via DI:

```python
@bot.message()
async def handler(message: Message, bot: Bot) -> None:
    rows = await bot.db.fetch("SELECT * FROM users")
```

## HTTP client

```python
import aiohttp
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(bot):
    async with aiohttp.ClientSession() as session:
        bot.http = session
        yield
    # session closes automatically here
```

## Multiple resources

```python
@asynccontextmanager
async def lifespan(bot):
    # open all resources
    bot.db = await asyncpg.create_pool(dsn=DATABASE_URL)
    bot.redis = await aioredis.from_url(REDIS_URL)
    async with aiohttp.ClientSession() as session:
        bot.http = session
        yield
    # cleanup in reverse order
    await bot.redis.close()
    await bot.db.close()
```

## skip_updates

Skip accumulated updates from while the bot was offline:

```python
bot.run_polling(skip_updates=True)
```
