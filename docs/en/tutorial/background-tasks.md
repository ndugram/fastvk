# Background Tasks

Run code **after** the handler returns — useful for slow operations that shouldn't block the response (logging, sending notifications, calling external APIs, etc.).

The API is identical to FastAPI's `BackgroundTasks`.

## Basic usage

```python
from fastvk import BackgroundTasks
from fastvk.types import Message

async def write_log(user_id: int, text: str) -> None:
    # runs after message.answer() already sent
    await some_db.insert(user_id=user_id, text=text)

@router.message()
async def handler(message: Message, background: BackgroundTasks) -> None:
    background.add_task(write_log, message.from_id, message.text)
    await message.answer("Got it!")
```

Declare `background: BackgroundTasks` as a parameter — FastVK injects it automatically. Call `background.add_task(func, *args, **kwargs)` before the handler returns. All tasks run concurrently after the handler finishes.

## Multiple tasks

```python
@router.message()
async def handler(message: Message, background: BackgroundTasks) -> None:
    background.add_task(log_message, message)
    background.add_task(update_stats, message.from_id)
    background.add_task(notify_admin, message.text)
    await message.answer("Processing!")
```

Tasks execute in the order they were added.

## Sync functions

```python
def sync_log(user_id: int) -> None:
    print(f"user {user_id} sent a message")

@router.message()
async def handler(message: Message, background: BackgroundTasks) -> None:
    background.add_task(sync_log, message.from_id)
    await message.answer("OK")
```

Both sync and async functions are supported.

## Passing to other functions

```python
async def process(message: Message, background: BackgroundTasks) -> None:
    background.add_task(log_message, message)

@router.message()
async def handler(message: Message, background: BackgroundTasks) -> None:
    await process(message, background)
    await message.answer("Done")
```

Pass `BackgroundTasks` as a regular argument to helper functions.

## Errors in background tasks

If a background task raises an exception it is logged (`fastvk.background` logger) and the remaining tasks still run.

```python
import logging
logging.getLogger("fastvk.background").setLevel(logging.ERROR)
```
