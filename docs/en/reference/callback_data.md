# CallbackData

Typed callback data factory — inspired by aiogram's `CallbackData`.

```python
from fastvk import CallbackData
```

## Defining a callback

```python
from typing import ClassVar
from fastvk import CallbackData


class BuyCallback(CallbackData):
    prefix: ClassVar[str] = "buy"
    item_id: int
    count: int = 1
```

`prefix` is a :class:`~typing.ClassVar` — it is not sent in the payload but is
used as a namespace prefix in the packed string for routing.

## pack

```python
cb = BuyCallback(item_id=5, count=2)
payload = cb.pack()
```

Returns a compact JSON string with the prefix:

```
buy:{"item_id":5,"count":2}
```

Pass the result directly to `Button.callback()`:

```python
Button.callback("Buy", payload=payload)
```

## unpack

```python
cb = BuyCallback.unpack(callback.payload)
```

Restores the typed object from `CallbackQuery.payload` (str or dict).

```python
@bot.callback()
async def on_buy(callback: CallbackQuery) -> None:
    cb = BuyCallback.unpack(callback.payload)
    await callback.answer(f"Bought {cb.count}x item #{cb.item_id}")
```

## Multiple callback types

Different prefixes keep them separate:

```python
class BuyCallback(CallbackData):
    prefix: ClassVar[str] = "buy"
    item_id: int

class VoteCallback(CallbackData):
    prefix: ClassVar[str] = "vote"
    rating: int


BuyCallback(item_id=5).pack()   # 'buy:{"item_id":5}'
VoteCallback(rating=3).pack()   # 'vote:{"rating":3}'
```

## API

### `pack() -> str`

Serialize the instance to a prefixed JSON string.

### `unpack(value: str | dict) -> Self`

Deserialize from a string (with or without prefix) or a dict.
