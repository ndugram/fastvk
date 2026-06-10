# Command Arguments

When a `Command` filter matches, FastVK automatically parses the arguments after the command and injects a `CommandArgs` object into your handler via DI.

## Basic usage

```python
from fastvk.filters import Command, CommandArgs
from fastvk.types import Message

@router.message(Command("ban"))
async def ban(message: Message, args: CommandArgs) -> None:
    if not args:
        await message.answer("Usage: /ban <user_id> [reason]")
        return
    user_id = args[0]
    reason  = args.get(1, "no reason")
    await message.answer(f"Banned {user_id}. Reason: {reason}")
```

Send `/ban 123456 spam` → `args[0]="123456"`, `args[1]="spam"`.

## Accessing arguments

```python
args[0]              # first arg — raises IndexError if missing
args.get(0)          # first arg — returns "" if missing
args.get(0, "anon")  # first arg — returns "anon" if missing
args.text            # raw string: "123456 spam"
args.command         # command name: "ban"
len(args)            # number of args
bool(args)           # False when no args provided
```

## Guard against missing args

```python
@router.message(Command("roll"))
async def roll(message: Message, args: CommandArgs) -> None:
    import random
    sides = int(args[0]) if args and args[0].isdigit() else 6
    await message.answer(f"🎲 {random.randint(1, sides)}")
```

## Full argument string

Use `args.text` when you need everything after the command as one string:

```python
@router.message(Command("say"))
async def say(message: Message, args: CommandArgs) -> None:
    if not args:
        await message.answer("Usage: /say <text>")
        return
    await message.answer(args.text)
```

## @mention stripping

`/ban@botname 123` and `/ban 123` both produce `args=("123",)` — the `@botname` part is stripped automatically.

## Import

```python
from fastvk.filters import CommandArgs
```
