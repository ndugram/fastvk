# Keyboard

## Button

```python
from fastvk.keyboard import Button
from fastvk.enums import Color
```

### Button.text

```python
Button.text(
    label: str,
    *,
    color: Color | str = Color.PRIMARY,
    payload: dict | str | None = None,
) -> Button
```

Создаёт обычную кнопку клавиатуры, которая отправляет текстовое сообщение.

### Button.callback

```python
Button.callback(
    label: str,
    *,
    payload: dict | str | None = None,
) -> Button
```

Создаёт inline (callback) кнопку, которая вызывает `message_event`.

### Button.link

```python
Button.link(label: str, *, url: str) -> Button
```

Создаёт кнопку-ссылку. Открывает URL в браузере.

### Button.location

```python
Button.location() -> Button
```

Создаёт кнопку запроса геолокации пользователя.

## Color

```python
from fastvk.enums import Color

Color.PRIMARY    # "primary"   — синий
Color.SECONDARY  # "secondary" — белый
Color.POSITIVE   # "positive"  — зелёный
Color.NEGATIVE   # "negative"  — красный
```

## Keyboard

```python
from fastvk.keyboard import Keyboard
```

### Конструктор

```python
Keyboard(
    one_time: bool = False,
    inline: bool = False,
)
```

| Параметр | Описание |
|---|---|
| `one_time` | Скрыть клавиатуру после первого нажатия |
| `inline` | Прикрепить клавиатуру к сообщению (inline режим) |

### Методы

```python
kb.row(*buttons: Button) -> Keyboard
```
Добавить новый ряд с кнопками. Возвращает `self` для цепочки вызовов.

```python
kb.add(*buttons: Button) -> Keyboard
```
Добавить кнопки в последний ряд (создаёт первый ряд если пустой). Возвращает `self`.

```python
kb.build() -> str
```
Сериализовать в JSON строку клавиатуры VK.

```python
str(kb) -> str
```
Псевдоним для `kb.build()`.

```python
Keyboard.remove() -> str
```
Вернуть JSON строку которая убирает клавиатуру из чата.

### Пример

```python
from fastvk.keyboard import Button, Keyboard
from fastvk.enums import Color

kb = (
    Keyboard(one_time=True)
    .row(
        Button.text("Да",  color=Color.POSITIVE),
        Button.text("Нет", color=Color.NEGATIVE),
    )
    .row(Button.text("Отмена"))
)

await message.answer("Подтверди?", keyboard=kb)
```
