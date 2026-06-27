# Фильтры

Фильтры решают, должен ли хэндлер обработать событие. Любой callable возвращающий истинное значение — проходит.

## Встроенные фильтры

### Command

```python
from fastvk.filters import Command

Command("start")                          # совпадает с /start
Command("start", "help")                  # совпадает с /start или /help
Command("ban", prefix="/!")               # совпадает с /ban и !ban
Command("buy", prefix="/")               # совпадает с /buy
```

### CommandArgs

`CommandArgs` инжектируется DI-системой автоматически, когда фильтр `Command` совпадает. Объяви его как параметр хэндлера — получишь распарсенные аргументы.

```python
from fastvk.filters import Command, CommandArgs

@router.message(Command("ban"))
async def ban(message: Message, args: CommandArgs) -> None:
    user_id = args[0]              # первый аргумент
    reason  = args.get(1, "-")    # второй или дефолт
    await message.answer(f"ban {user_id}: {reason}")
```

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `command` | `str` | Имя команды без префикса |
| `args` | `tuple[str, ...]` | Аргументы, разбитые по пробелу |
| `text` | `str` | Сырая строка аргументов после команды |

| Метод / оператор | Описание |
|------------------|----------|
| `args[n]` | n-й аргумент (бросает `IndexError` если нет) |
| `args.get(n, default="")` | n-й аргумент с запасным значением |
| `len(args)` | Количество аргументов |
| `bool(args)` | `False` если аргументов нет |

`/ban@botname 123 спам` → `command="ban"`, `args=("123", "спам")`, `text="123 спам"`

### CommandStart / CommandHelp

```python
from fastvk.filters import CommandStart, CommandHelp

@bot.message(CommandStart())
async def start_handler(message): ...

@bot.message(CommandHelp())
async def help_handler(message): ...
```

### StateFilter

```python
from fastvk.filters import StateFilter
from fastvk.fsm import State, StatesGroup

class Form(StatesGroup):
    waiting_name = State()

@bot.message(StateFilter(Form.waiting_name))
async def handler(message, state): ...

# совпадает с любым не-None состоянием:
@bot.message(StateFilter("*"))
async def any_state_handler(message): ...
```

### Text

```python
from fastvk.filters import Text

Text("hello")                # точное совпадение
Text("hello", "hi")          # любое из этих
Text(contains="world")       # совпадение подстроки
Text(startswith="!")          # совпадение с началом
```

### CallbackDataFilter

Фильтрует колбэки по типу :class:`~fastvk.CallbackData`. Автоматически распаковывает payload и инжектит типизированный объект через DI.

```python
from fastvk.filters import CallbackDataFilter
from fastvk import CallbackData


class BuyCallback(CallbackData):
    prefix: ClassVar[str] = "buy"
    item_id: int


@bot.callback(CallbackDataFilter(BuyCallback))
async def on_buy(callback: CallbackQuery, callback_data: BuyCallback) -> None:
    await callback.answer(f"Товар #{callback_data.item_id}")
```

## F — Magic filter

`F` строит ленивые выражения фильтрации через доступ к атрибутам и операторы.

```python
from fastvk import F
```

### Доступ к атрибутам

```python
F.text          # message.text
F.from_id       # message.from_id
F.payload       # callback.payload (dict)
F.payload.vote  # callback.payload["vote"]
```

### Сравнения

```python
F.text == "hello"
F.text != "bye"
F.from_id > 0
```

### Строковые методы

```python
F.text.startswith("/")
F.text.endswith("!")
F.text.contains("vk")
F.text.regexp(r"^\d+$")     # regex совпадение (re.search)
```

### Принадлежность

```python
F.from_id.in_(1, 2, 3)
F.text.in_("yes", "да", "y")
```

### Существование

```python
F.payload.exists()    # значение не None
F.text.exists()
```

### Логика

```python
~F.text.startswith("/")              # НЕ
(F.text == "a") | (F.text == "b")   # ИЛИ
(F.from_id > 0) & F.text.exists()   # И
```

## Кастомные фильтры

Подходит любой callable:

```python
def is_admin(message: Message, data: dict) -> bool:
    return message.from_id in ADMIN_IDS

@bot.message(is_admin)
async def admin_cmd(message): ...
```

Или класс:

```python
class IsAdmin:
    def __init__(self, *ids: int) -> None:
        self._ids = set(ids)

    def __call__(self, message: Message, data: dict) -> bool:
        return message.from_id in self._ids

@bot.message(IsAdmin(111, 222))
async def admin_cmd(message): ...
```
