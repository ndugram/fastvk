# Исключения

FastVK имеет небольшую, сфокусированную иерархию исключений.

## Иерархия

```
FastVKError
├── VKAPIError           — VK вернул код ошибки
├── HandlerNotFoundError — ни один хэндлер не совпал с апдейтом
├── FilterError          — фильтр завершился с ошибкой
├── StorageError         — ошибка чтения/записи FSM хранилища
└── PollingError         — long-poll запрос провалился
```

## VKAPIError

Вызывается когда VK API возвращает `{"error": {...}}`:

```python
from fastvk.exceptions import VKAPIError

try:
    await bot.messages.send(peer_id=123, message="Привет", random_id=0)
except VKAPIError as e:
    print(e.error_code)     # int, например 7
    print(e.error_msg)      # str, например "Permission to perform this action is denied"
    print(e.request_params) # list[dict]
```

Частые коды ошибок:

| Код | Значение |
|---|---|
| 5 | Неверный токен |
| 7 | Нет прав |
| 9 | Flood control (слишком много отправок) |
| 100 | Неверный параметр |
| 914 | Сообщение слишком длинное |

## Перехват ошибок в хэндлерах

```python
from fastvk.exceptions import VKAPIError

@bot.message()
async def handler(message: Message) -> None:
    try:
        await message.answer("Привет!")
    except VKAPIError as e:
        if e.error_code == 9:
            # flood control — подождать
            await asyncio.sleep(1)
```

## Глобальный обработчик ошибок

Зарегистрируй обработчик, который перехватывает исключения из любого хэндлера:

```python
@bot.error()
async def on_error(error: Exception, message: Message) -> None:
    print(f"Ошибка при обработке {message.id}: {error}")
    await message.answer("Что-то пошло не так. Попробуй ещё раз.")
```

Параметр `message: Message` разрешается через DI — используй `CallbackQuery` для ошибок callback.

## HandlerNotFoundError

Вызывается когда ни один хэндлер не совпал с апдейтом. Обычно можно игнорировать (необработанные апдейты по умолчанию пропускаются тихо).

## StorageError

Вызывается при сбое FSM хранилища (например Redis отвалился):

```python
from fastvk.exceptions import StorageError

@bot.error()
async def on_error(error: Exception) -> None:
    if isinstance(error, StorageError):
        # переподключиться или откатиться на MemoryStorage
        ...
```
