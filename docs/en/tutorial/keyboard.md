# Keyboard

FastVK provides `Button` and `Keyboard` classes for building VK keyboards.

## Button types

```python
from fastvk.keyboard import Button
from fastvk.enums import Color

# Text button (regular keyboard)
Button.text("Click me")
Button.text("Yes", color=Color.POSITIVE)
Button.text("No",  color=Color.NEGATIVE)
Button.text("Back", color=Color.PRIMARY, payload={"cmd": "back"})

# Callback button (inline keyboard — triggers message_event)
Button.callback("Like 👍", payload={"vote": 1})
Button.callback("Dislike 👎", payload={"vote": 0})

# Link button
Button.link("GitHub", url="https://github.com")

# Location button (requests user's location)
Button.location()

# VK Pay button
Button.vkpay(action="pay-to-group", group_id=123, amount=100, description="Donation")
Button.vkpay(action="transfer-to-group", group_id=123, aid=1)
Button.vkpay(action="transfer-to-user", user_id=456, aid=1)
```

### VK Pay button

`Button.vkpay` builds the internal `hash` string from typed parameters — no manual string construction needed.

```python
# Payment to group (most common)
Button.vkpay(
    action="pay-to-group",
    group_id=123456,
    amount=100,           # rubles
    description="Donate",
)

# Transfer to group
Button.vkpay(action="transfer-to-group", group_id=123456, aid=1)

# Transfer to user
Button.vkpay(action="transfer-to-user", user_id=654321, aid=1)
```

| Parameter | Required for | Description |
|---|---|---|
| `action` | all | `"pay-to-group"` / `"transfer-to-group"` / `"transfer-to-user"` |
| `group_id` | group actions | Target group ID |
| `user_id` | `transfer-to-user` | Target user ID |
| `amount` | `pay-to-group` | Amount in rubles |
| `description` | `pay-to-group` | Payment description |
| `merchant_id` | optional | Merchant identifier |
| `aid` | transfer actions | Additional ID |

!!! note
    VK Pay buttons only work on **inline** keyboards (`Keyboard(inline=True)`).

### Button colors

| Color | Value | Usage |
|---|---|---|
| `Color.PRIMARY` | `"primary"` | Blue — main action |
| `Color.SECONDARY` | `"secondary"` | White — secondary |
| `Color.POSITIVE` | `"positive"` | Green — confirm |
| `Color.NEGATIVE` | `"negative"` | Red — cancel/danger |

## Building a keyboard

```python
from fastvk.keyboard import Keyboard

# Regular keyboard with rows
kb = (
    Keyboard(one_time=True)
    .row(Button.text("✅ Yes", color=Color.POSITIVE),
         Button.text("❌ No",  color=Color.NEGATIVE))
    .row(Button.text("Cancel"))
)

await message.answer("Choose:", keyboard=kb)
```

```python
# Inline keyboard
kb = (
    Keyboard(inline=True)
    .row(Button.callback("👍", payload={"v": 1}),
         Button.callback("👎", payload={"v": 0}))
)

await message.answer("Rate:", keyboard=kb)
```

### Keyboard parameters

| Parameter | Default | Description |
|---|---|---|
| `one_time` | `False` | Hide keyboard after one press |
| `inline` | `False` | Inline keyboard (attached to the message) |

### Methods

```python
kb.row(*buttons)    # add a new row with buttons
kb.add(*buttons)    # add buttons to the last row
kb.build()          # serialize to JSON string
str(kb)             # same as build()
Keyboard.remove()   # JSON string that removes the keyboard
```

## Remove keyboard

```python
await message.answer("Keyboard removed", keyboard=Keyboard.remove())
```

## Full example

```python
from fastvk import FastVK, CommandStart, F
from fastvk.keyboard import Button, Keyboard
from fastvk.types import Message, CallbackQuery
from fastvk.enums import Color

bot = FastVK(token="...", group_id=123)

menu_kb = (
    Keyboard(inline=True)
    .row(
        Button.callback("🛒 Catalog", payload={"action": "catalog"}),
        Button.callback("📦 My orders", payload={"action": "orders"}),
    )
    .row(Button.callback("📞 Support", payload={"action": "support"}))
)


@bot.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Main menu:", keyboard=menu_kb)


@bot.callback(F.payload.action == "catalog")
async def on_catalog(callback: CallbackQuery) -> None:
    await callback.answer("Opening catalog...")


@bot.callback(F.payload.action == "orders")
async def on_orders(callback: CallbackQuery) -> None:
    await callback.answer("Your orders are empty")


bot.run_polling()
```
