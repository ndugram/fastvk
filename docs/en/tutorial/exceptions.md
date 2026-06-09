# Exceptions

FastVK has a small, focused exception hierarchy.

## Exception hierarchy

```
FastVKError
├── VKAPIError          — VK returned an error code
├── HandlerNotFoundError — no handler matched the update
├── FilterError         — filter raised unexpectedly
├── StorageError        — FSM storage read/write failed
└── PollingError        — long-poll request failed
```

## VKAPIError

Raised when VK API returns `{"error": {...}}`:

```python
from fastvk.exceptions import VKAPIError

try:
    await bot.messages.send(peer_id=123, message="Hi", random_id=0)
except VKAPIError as e:
    print(e.error_code)    # int, e.g. 7
    print(e.error_msg)     # str, e.g. "Permission to perform this action is denied"
    print(e.request_params) # list[dict]
```

Common error codes:

| Code | Meaning |
|---|---|
| 5 | Invalid token |
| 7 | No permission |
| 9 | Flood control (too many sends) |
| 100 | Invalid parameter |
| 914 | Message too long |

## Catching errors in handlers

```python
from fastvk.exceptions import VKAPIError

@bot.message()
async def handler(message: Message) -> None:
    try:
        await message.answer("Hello!")
    except VKAPIError as e:
        if e.error_code == 9:
            # flood control — back off
            await asyncio.sleep(1)
```

## Global error handler

Register an error handler that catches exceptions from any handler:

```python
@bot.error()
async def on_error(error: Exception, message: Message) -> None:
    print(f"Error handling {message.id}: {error}")
    await message.answer("Something went wrong. Try again.")
```

The `message: Message` parameter is resolved by DI — use `CallbackQuery` for callback errors.

## HandlerNotFoundError

Raised when no handler matches an update. Usually safe to ignore (unhandled updates are silently skipped by default).

## StorageError

Raised when FSM storage fails (e.g. Redis disconnected):

```python
from fastvk.exceptions import StorageError

@bot.error()
async def on_error(error: Exception) -> None:
    if isinstance(error, StorageError):
        # reconnect or fallback to MemoryStorage
        ...
```
