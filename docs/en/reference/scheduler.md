# Scheduler

```python
from fastvk import Scheduler
```

In-process interval / daily scheduler that shares the bot's event loop.

## Decorators

### @scheduler.every

```python
@scheduler.every(interval: float | str, *, name: str | None = None)
async def job() -> None: ...
```

Run repeatedly. `interval` is seconds, or a string: `"45s"`, `"5m"`, `"2h"`, `"1d"`.

### @scheduler.at

```python
@scheduler.at("HH:MM", *, name: str | None = None)
async def job() -> None: ...
```

Run once per day at the given local time.

## Methods

| Method | Description |
|---|---|
| `add_job(func, interval, *args, name=None, **kwargs)` | Register a job imperatively |
| `bind(*objects)` | Register objects injectable into jobs by type |
| `await start()` | Start the scheduler loop (idempotent) |
| `await stop()` | Cancel the loop |

## Dependency injection

A job with type-annotated parameters receives any object passed to
`scheduler.bind(...)` whose type matches. Jobs created with positional/keyword
arguments via `add_job` are not injected.

```python
scheduler.bind(bot)

@scheduler.every("30m")
async def refresh(bot: FastVK) -> None:
    ...
```

## Wiring into a bot

```python
@bot.startup
async def _start(bot: FastVK) -> None:
    scheduler.bind(bot)
    await scheduler.start()

@bot.shutdown
async def _stop() -> None:
    await scheduler.stop()
```

Job exceptions are logged (`fastvk.scheduler`) and never stop the loop.
Timing granularity is ~1 second.
