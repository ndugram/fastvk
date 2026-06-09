# Filters

Filters determine whether a handler should process an incoming event. Pass them as arguments to `@bot.message()` or any other decorator.

## Command

Matches messages that start with a bot command.

```python
from fastvk import Command

@bot.message(Command("start"))
async def on_start(message: Message) -> None:
    await message.answer("Hello!")

# multiple commands in one handler
@bot.message(Command("help", "faq", "info"))
async def on_help(message: Message) -> None:
    await message.answer("Help text here")
```

Handles all forms: `/start`, `/start@mybot`, `/start argument`.

### Custom prefix

```python
# matches !ban and /ban
@bot.message(Command("ban", "kick", prefix="!/"))
async def mod_cmd(message: Message) -> None:
    ...
```

`prefix` is a string where each character is a valid prefix.

## CommandStart / CommandHelp

Shortcuts for the most common commands:

```python
from fastvk import CommandStart, CommandHelp

@bot.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Welcome!")

@bot.message(CommandHelp())
async def help_cmd(message: Message) -> None:
    await message.answer("Here's what I can do...")
```

## Text

Matches message text exactly or by substring.

```python
from fastvk.filters import Text

@bot.message(Text("hello"))
async def on_hello(message: Message) -> None:
    await message.answer("Hi!")

# case-sensitive exact match
@bot.message(Text("HELLO", ignore_case=False))
async def case_sensitive(message: Message) -> None: ...

# substring match
@bot.message(Text("discount", contains=True, ignore_case=True))
async def on_promo(message: Message) -> None:
    await message.answer("Here's your promo code!")

# multiple values
@bot.message(Text("yes", "yeah", "yep"))
async def on_yes(message: Message) -> None: ...
```

| Parameter | Default | Description |
|---|---|---|
| `*texts` | — | Text values to match |
| `contains` | `False` | Substring match instead of exact |
| `ignore_case` | `True` | Case-insensitive comparison |

## F — magic filter

`F` builds lazy attribute-based filter expressions with full IDE support.

```python
from fastvk import F

# equality
@bot.message(F.text == "hello")
async def on_hello(message: Message) -> None: ...

# inequality
@bot.message(F.text != "")
async def non_empty(message: Message) -> None: ...

# substring
@bot.message(F.text.contains("deal"))
async def on_deal(message: Message) -> None: ...

# startswith / endswith
@bot.message(F.text.startswith("/"))
async def any_command(message: Message) -> None: ...

# in_ — one of values
@bot.message(F.from_id.in_(111, 222, 333))
async def admins_only(message: Message) -> None: ...

# regexp
@bot.message(F.text.regexp(r"^\d+$"))
async def digits_only(message: Message) -> None:
    await message.answer(f"Got number: {message.text}")

# nested attributes
@bot.callback(F.payload == {"action": "buy"})
async def on_buy(callback: CallbackQuery) -> None: ...

@bot.callback(F.payload.action == "buy")
async def on_buy2(callback: CallbackQuery) -> None: ...
```

### Combining filters with `&`, `|`, `~`

```python
# AND
@bot.message(F.text.contains("buy") & F.from_id.in_(VIP_IDS))
async def vip_buy(message: Message) -> None: ...

# OR
@bot.message(F.text.contains("sale") | F.text.contains("promo"))
async def on_promo(message: Message) -> None: ...

# NOT
@bot.message(~F.text.startswith("/"))
async def not_command(message: Message) -> None: ...
```

## StateFilter

Matches only when the user is in a specific FSM state. See [FSM](fsm.md) for the full guide.

```python
from fastvk.filters import StateFilter
from fastvk.fsm import State, StatesGroup


class Form(StatesGroup):
    waiting_name = State()
    waiting_age = State()


@bot.message(StateFilter(Form.waiting_name))
async def got_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.waiting_age)
    await message.answer("How old are you?")
```

## FromUser / IsChat

```python
from fastvk.filters import FromUser, IsChat

# only from specific user ID
@bot.message(FromUser(123456))
async def from_vip(message: Message) -> None: ...

# only in group chats (peer_id > 2_000_000_000)
@bot.message(IsChat())
async def chat_only(message: Message) -> None: ...
```
