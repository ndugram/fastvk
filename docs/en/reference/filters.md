# Filters

Filters decide whether a handler should process an event. Any callable returning a truthy value passes.

## Built-in filters

### Command

```python
from fastvk.filters import Command

Command("start")                          # matches /start
Command("start", "help")                  # matches /start or /help
Command("ban", prefix="/!")               # matches /ban and !ban
Command("buy", prefix="/")               # matches /buy
```

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

# match any non-None state:
@bot.message(StateFilter("*"))
async def any_state_handler(message): ...
```

### Text

```python
from fastvk.filters import Text

Text("hello")                # exact match
Text("hello", "hi")          # any of these
Text(contains="world")       # substring match
Text(startswith="!")          # prefix match
```

## F — Magic filter

`F` builds lazy filter expressions from attribute access and operators.

```python
from fastvk import F
```

### Attribute access

```python
F.text          # message.text
F.from_id       # message.from_id
F.payload       # callback.payload (dict)
F.payload.vote  # callback.payload["vote"]
```

### Comparisons

```python
F.text == "hello"
F.text != "bye"
F.from_id > 0
```

### String methods

```python
F.text.startswith("/")
F.text.endswith("!")
F.text.contains("vk")
F.text.regexp(r"^\d+$")     # regex match (re.search)
```

### Membership

```python
F.from_id.in_(1, 2, 3)
F.text.in_("yes", "да", "y")
```

### Existence

```python
F.payload.exists()    # value is not None
F.text.exists()
```

### Logic

```python
~F.text.startswith("/")              # NOT
(F.text == "a") | (F.text == "b")   # OR
(F.from_id > 0) & F.text.exists()   # AND
```

## Custom filters

Any callable works:

```python
def is_admin(message: Message, data: dict) -> bool:
    return message.from_id in ADMIN_IDS

@bot.message(is_admin)
async def admin_cmd(message): ...
```

Or a class:

```python
class IsAdmin:
    def __init__(self, *ids: int) -> None:
        self._ids = set(ids)

    def __call__(self, message: Message, data: dict) -> bool:
        return message.from_id in self._ids

@bot.message(IsAdmin(111, 222))
async def admin_cmd(message): ...
```
