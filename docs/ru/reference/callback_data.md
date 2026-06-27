# CallbackData

Типизированная фабрика callback данных — по мотивам aiogram `CallbackData`.

```python
from fastvk import CallbackData
```

## Определение

```python
from typing import ClassVar
from fastvk import CallbackData


class BuyCallback(CallbackData):
    prefix: ClassVar[str] = "buy"
    item_id: int
    count: int = 1
```

`prefix` — это :class:`~typing.ClassVar`. Он не попадает в полезную нагрузку,
но служит пространством имён в сериализованной строке для удобства роутинга.

## pack

```python
cb = BuyCallback(item_id=5, count=2)
payload = cb.pack()
```

Возвращает компактную JSON-строку с префиксом:

```
buy:{"item_id":5,"count":2}
```

Результат передаётся напрямую в `Button.callback()`:

```python
Button.callback("Купить", payload=payload)
```

## unpack

```python
cb = BuyCallback.unpack(callback.payload)
```

Восстанавливает типизированный объект из `CallbackQuery.payload` (строка или dict).

```python
@bot.callback()
async def on_buy(callback: CallbackQuery) -> None:
    cb = BuyCallback.unpack(callback.payload)
    await callback.answer(f"Куплено {cb.count}x товар #{cb.item_id}")
```

## Несколько типов

Разные префиксы предотвращают конфликты:

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

Сериализует экземпляр в JSON-строку с префиксом.

### `unpack(value: str | dict) -> Self`

Десериализует из строки (с префиксом или без) либо из словаря.
