# Аргументы команд

Когда фильтр `Command` совпадает, FastVK автоматически парсит аргументы после команды и инжектирует объект `CommandArgs` в хэндлер через DI.

## Базовое использование

```python
from fastvk.filters import Command, CommandArgs
from fastvk.types import Message

@router.message(Command("ban"))
async def ban(message: Message, args: CommandArgs) -> None:
    if not args:
        await message.answer("Использование: /ban <user_id> [причина]")
        return
    user_id = args[0]
    reason  = args.get(1, "без причины")
    await message.answer(f"Заблокирован {user_id}. Причина: {reason}")
```

`/ban 123456 спам` → `args[0]="123456"`, `args[1]="спам"`.

## Доступ к аргументам

```python
args[0]              # первый арг — бросит IndexError если нет
args.get(0)          # первый арг — вернёт "" если нет
args.get(0, "anon")  # первый арг — вернёт "anon" если нет
args.text            # сырая строка: "123456 спам"
args.command         # имя команды: "ban"
len(args)            # количество аргументов
bool(args)           # False если аргументов нет
```

## Защита от отсутствующих аргументов

```python
@router.message(Command("roll"))
async def roll(message: Message, args: CommandArgs) -> None:
    import random
    sides = int(args[0]) if args and args[0].isdigit() else 6
    await message.answer(f"🎲 {random.randint(1, sides)}")
```

## Полная строка аргументов

Используй `args.text` когда нужно всё после команды одной строкой:

```python
@router.message(Command("say"))
async def say(message: Message, args: CommandArgs) -> None:
    if not args:
        await message.answer("Использование: /say <текст>")
        return
    await message.answer(args.text)
```

## Стрипинг @упоминания

`/ban@botname 123` и `/ban 123` оба дают `args=("123",)` — `@botname` срезается автоматически.

## Импорт

```python
from fastvk.filters import CommandArgs
```
