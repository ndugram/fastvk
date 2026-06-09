# Исключения

## Иерархия

```
FastVKError (базовый)
├── VKAPIError
├── HandlerNotFoundError
├── FilterError
├── StorageError
└── PollingError
```

Все исключения наследуют `FastVKError`, который наследует `Exception`.

## FastVKError

```python
from fastvk.exceptions import FastVKError
```

Базовый класс. Перехвати его чтобы обработать любую ошибку FastVK.

## VKAPIError

```python
from fastvk.exceptions import VKAPIError

class VKAPIError(FastVKError):
    error_code: int
    error_msg: str
    request_params: list[dict]
```

Вызывается когда VK API возвращает `{"error": {...}}`.

```python
try:
    await bot.messages.send(...)
except VKAPIError as e:
    print(e.error_code, e.error_msg)
```

Частые коды:

| Код | Значение |
|---|---|
| 5 | Неверный или истёкший токен |
| 7 | Отказано в правах |
| 9 | Достигнут лимит flood control |
| 100 | Неверное значение параметра |
| 914 | Текст сообщения слишком длинный |

## HandlerNotFoundError

```python
from fastvk.exceptions import HandlerNotFoundError
```

Вызывается когда ни один хэндлер не совпал с входящим апдейтом. По умолчанию бот молча пропускает такие апдейты.

## FilterError

```python
from fastvk.exceptions import FilterError
```

Вызывается когда фильтр выбрасывает неожиданное исключение во время вычисления.

## StorageError

```python
from fastvk.exceptions import StorageError
```

Вызывается при сбое операций FSM хранилища (ошибка подключения, ошибка сериализации и т.д.).

## PollingError

```python
from fastvk.exceptions import PollingError
```

Вызывается когда сам long-poll запрос проваливается (сетевая ошибка, неверный ответ сервера). Цикл polling автоматически повторяет попытки с задержкой.
