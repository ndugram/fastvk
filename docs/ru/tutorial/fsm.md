# FSM — конечный автомат состояний

FSM позволяет строить многошаговые диалоги, где пользователь проходит через последовательность состояний.

## Объявление состояний

```python
from fastvk.fsm import State, StatesGroup


class Form(StatesGroup):
    waiting_name = State()   # "Form:waiting_name"
    waiting_age  = State()   # "Form:waiting_age"
    waiting_city = State()   # "Form:waiting_city"
```

Каждый `State` получает имя автоматически из названия класса и атрибута.

## Использование FSMContext

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
    await message.answer("Как тебя зовут?")


@bot.message(StateFilter(Form.waiting_name))
async def got_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.waiting_age)
    await message.answer("Сколько тебе лет?")


@bot.message(StateFilter(Form.waiting_age))
async def got_age(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    await message.answer(
        f"Имя: {data['name']}\nВозраст: {message.text}\nРегистрация завершена!"
    )


bot.run_polling()
```

## API FSMContext

```python
# установить состояние
await state.set_state(Form.waiting_name)   # объект State
await state.set_state("Form:waiting_name") # или строка
await state.set_state(None)               # только очистить состояние

# получить состояние
current = await state.get_state()   # str | None

# сохранить данные
await state.update_data(name="Алиса", age=25)  # слияние
await state.set_data({"name": "Алиса"})         # замена

# прочитать данные
data = await state.get_data()   # dict

# сбросить всё
await state.clear()   # state → None, data → {}
```

## Хранилища

### MemoryStorage (по умолчанию)

Данные живут в памяти процесса. Теряются при перезапуске. Подходит для разработки.

```python
from fastvk.fsm import MemoryStorage

bot = FastVK(token="...", group_id=123, storage=MemoryStorage())
```

### RedisStorage

Данные сохраняются между перезапусками. Требует `pip install fastvk[redis]`.

```python
from fastvk.fsm.redis import RedisStorage

bot = FastVK(
    token="...",
    group_id=123,
    storage=RedisStorage.from_url("redis://localhost:6379/0"),
)
```

Кастомный префикс (чтобы не конфликтовать с другими приложениями):

```python
storage = RedisStorage.from_url(
    "redis://localhost:6379/0",
    prefix="mybot",
)
```

## Отмена состояния

Всегда давай пользователям возможность отменить текущий диалог:

```python
from fastvk import Command

@bot.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current is None:
        await message.answer("Нечего отменять.")
        return
    await state.clear()
    await message.answer("Отменено.", keyboard=Keyboard.remove())
```
