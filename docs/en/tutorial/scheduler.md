# Scheduler

`Scheduler` runs coroutines on an interval or at a fixed daily time, in the
same event loop as the bot. No external dependencies.

```python
from fastvk import FastVK, Scheduler
from fastvk.types import Message

bot = FastVK(token="vk1.a.YOUR_TOKEN")
scheduler = Scheduler()


@scheduler.every("30m")
async def refresh() -> None:
    ...


@scheduler.at("09:00")
async def morning_digest() -> None:
    ...


@bot.startup
async def _start(bot: FastVK) -> None:
    scheduler.bind(bot)          # make `bot` injectable into jobs
    await scheduler.start()


@bot.shutdown
async def _stop() -> None:
    await scheduler.stop()


if __name__ == "__main__":
    bot.run_polling()
```

## Intervals

`every()` accepts seconds as a number, or a short string:

| String | Meaning |
|---|---|
| `"45s"` | 45 seconds |
| `"5m"` | 5 minutes |
| `"2h"` | 2 hours |
| `"1d"` | 1 day |

`at("HH:MM")` runs once per day at that local time.

## Dependency injection into jobs

`scheduler.bind(obj)` registers an object by its type. A job that declares a
matching parameter gets it:

```python
scheduler.bind(bot, db)

@scheduler.every("1h")
async def cleanup(bot: FastVK, db: Database) -> None:
    ...
```

## Manual jobs

```python
scheduler.add_job(send_report, "12h", chat_id=2000000001, name="report")
```

## API

| Method | Description |
|---|---|
| `@scheduler.every(interval, *, name=None)` | Run repeatedly |
| `@scheduler.at("HH:MM", *, name=None)` | Run daily at a time |
| `scheduler.add_job(func, interval, *args, name=None, **kwargs)` | Register imperatively |
| `scheduler.bind(*objects)` | Register injectables by type |
| `await scheduler.start()` / `await scheduler.stop()` | Control the loop |
