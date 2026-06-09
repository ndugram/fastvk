# FSM — Finite State Machine

FSM lets you build multi-step conversations where a user goes through a sequence of states.

## Defining states

```python
from fastvk.fsm import State, StatesGroup


class Form(StatesGroup):
    waiting_name = State()   # "Form:waiting_name"
    waiting_age  = State()   # "Form:waiting_age"
    waiting_city = State()   # "Form:waiting_city"
```

Each `State` gets its name automatically from the class and attribute names.

## Using FSMContext

```python
from fastvk import FastVK, CommandStart
from fastvk.types import Message
from fastvk.fsm import FSMContext, State, StatesGroup
from fastvk.filters import StateFilter

bot = FastVK(token="...", group_id=123)


class Form(StatesGroup):
    waiting_name = State()
    waiting_age  = State()


@bot.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.waiting_name)
    await message.answer("What's your name?")


@bot.message(StateFilter(Form.waiting_name))
async def got_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.waiting_age)
    await message.answer("How old are you?")


@bot.message(StateFilter(Form.waiting_age))
async def got_age(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    await message.answer(
        f"Name: {data['name']}\nAge: {message.text}\nRegistration complete!"
    )


bot.run_polling()
```

## FSMContext API

```python
# set state
await state.set_state(Form.waiting_name)   # State object
await state.set_state("Form:waiting_name") # or raw string
await state.set_state(None)               # clear state only

# get state
current = await state.get_state()   # str | None

# store data
await state.update_data(name="Alice", age=25)  # merge
await state.set_data({"name": "Alice"})         # replace

# read data
data = await state.get_data()   # dict

# reset everything
await state.clear()   # state → None, data → {}
```

## Storages

### MemoryStorage (default)

Data lives in process memory. Lost on restart. Good for development.

```python
from fastvk.fsm import MemoryStorage

bot = FastVK(token="...", group_id=123, storage=MemoryStorage())
```

### RedisStorage

Data persists across restarts. Requires `pip install fastvk[redis]`.

```python
from fastvk.fsm.redis import RedisStorage

bot = FastVK(
    token="...",
    group_id=123,
    storage=RedisStorage.from_url("redis://localhost:6379/0"),
)
```

Custom prefix (to avoid key collisions with other apps):

```python
storage = RedisStorage.from_url(
    "redis://localhost:6379/0",
    prefix="mybot",
)
```

## Cancel state

Always give users a way to cancel the current flow:

```python
from fastvk import Command

@bot.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current is None:
        await message.answer("Nothing to cancel.")
        return
    await state.clear()
    await message.answer("Cancelled.", keyboard=Keyboard.remove())
```
