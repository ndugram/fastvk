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

Creates a regular keyboard button that sends a text message.

### Button.callback

```python
Button.callback(
    label: str,
    *,
    payload: dict | str | None = None,
) -> Button
```

Creates an inline (callback) button that triggers a `message_event`.

### Button.link

```python
Button.link(label: str, *, url: str) -> Button
```

Creates a link button. Opens URL in browser.

### Button.location

```python
Button.location() -> Button
```

Creates a button that requests the user's geolocation.

## Color

```python
from fastvk.enums import Color

Color.PRIMARY    # "primary"   — blue
Color.SECONDARY  # "secondary" — white
Color.POSITIVE   # "positive"  — green
Color.NEGATIVE   # "negative"  — red
```

## Keyboard

```python
from fastvk.keyboard import Keyboard
```

### Constructor

```python
Keyboard(
    one_time: bool = False,
    inline: bool = False,
)
```

| Parameter | Description |
|---|---|
| `one_time` | Hide keyboard after first press |
| `inline` | Attach keyboard to the message (inline mode) |

### Methods

```python
kb.row(*buttons: Button) -> Keyboard
```
Add a new row with the given buttons. Returns `self` for chaining.

```python
kb.add(*buttons: Button) -> Keyboard
```
Add buttons to the last row (creates first row if empty). Returns `self`.

```python
kb.build() -> str
```
Serialize to VK keyboard JSON string.

```python
str(kb) -> str
```
Alias for `kb.build()`.

```python
Keyboard.remove() -> str
```
Return the JSON string that removes the keyboard from a chat.

### Example

```python
from fastvk.keyboard import Button, Keyboard
from fastvk.enums import Color

kb = (
    Keyboard(one_time=True)
    .row(
        Button.text("Yes", color=Color.POSITIVE),
        Button.text("No",  color=Color.NEGATIVE),
    )
    .row(Button.text("Cancel"))
)

await message.answer("Confirm?", keyboard=kb)
```
