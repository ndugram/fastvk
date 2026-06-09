# Exceptions

## Hierarchy

```
FastVKError (base)
├── VKAPIError
├── HandlerNotFoundError
├── FilterError
├── StorageError
└── PollingError
```

All exceptions inherit from `FastVKError`, which inherits from `Exception`.

## FastVKError

```python
from fastvk.exceptions import FastVKError
```

Base class. Catch this to handle any FastVK error.

## VKAPIError

```python
from fastvk.exceptions import VKAPIError

class VKAPIError(FastVKError):
    error_code: int
    error_msg: str
    request_params: list[dict]
```

Raised when the VK API returns `{"error": {...}}`.

```python
try:
    await bot.messages.send(...)
except VKAPIError as e:
    print(e.error_code, e.error_msg)
```

Common codes:

| Code | Meaning |
|---|---|
| 5 | Invalid or expired token |
| 7 | Permission denied |
| 9 | Flood control limit reached |
| 100 | Invalid parameter value |
| 914 | Message text too long |

## HandlerNotFoundError

```python
from fastvk.exceptions import HandlerNotFoundError
```

Raised when no handler matches an incoming update. The bot silently skips these by default.

## FilterError

```python
from fastvk.exceptions import FilterError
```

Raised when a filter raises an unexpected exception during evaluation.

## StorageError

```python
from fastvk.exceptions import StorageError
```

Raised when FSM storage operations fail (connection error, serialization failure, etc.).

## PollingError

```python
from fastvk.exceptions import PollingError
```

Raised when the long-poll request itself fails (network error, invalid server response). The polling loop retries automatically with backoff.
