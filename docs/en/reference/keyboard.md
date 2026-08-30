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

### Button.vkapps

```python
Button.vkapps(
    label: str,
    *,
    app_id: int,
    owner_id: int | None = None,
    hash: str = "",
    payload: dict | str | None = None,
) -> ButtonDict
```

Creates a button that opens a VK Mini App.

### Button.vkpay

```python
Button.vkpay(
    *,
    action: Literal["pay-to-group", "transfer-to-group", "transfer-to-user"] = "pay-to-group",
    group_id: int | None = None,
    user_id: int | None = None,
    amount: int | None = None,
    description: str = "",
    merchant_id: int | None = None,
    aid: int | None = None,
) -> ButtonDict
```

Creates a VK Pay button. Builds the `hash` parameter internally from the provided arguments.

Only works inside `Keyboard(inline=True)`.

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

## Carousel

```python
from fastvk import Carousel

Carousel().element(
    *,
    title: str = "",
    description: str = "",
    photo_id: str | None = None,
    buttons: list[ButtonDict] | None = None,
    link: str | None = None,
) -> Carousel
```

Builds a message `template` (`type: "carousel"`, ≤ 10 elements). `str(carousel)`
/ `carousel.build()` returns the JSON; pass it as `template=` to
`messages.send` or use `message.answer_carousel(...)`.

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
