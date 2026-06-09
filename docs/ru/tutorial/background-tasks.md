# Фоновые задачи

Запускай код **после** того как хендлер вернул ответ — для медленных операций, которые не должны блокировать ответ пользователю (логирование, отправка уведомлений, обращение к внешним API и т.д.).

API идентичен `BackgroundTasks` из FastAPI.

## Базовое использование

```python
from fastvk import BackgroundTasks
from fastvk.types import Message

async def write_log(user_id: int, text: str) -> None:
    # выполняется после того как message.answer() уже отправлен
    await some_db.insert(user_id=user_id, text=text)

@router.message()
async def handler(message: Message, background: BackgroundTasks) -> None:
    background.add_task(write_log, message.from_id, message.text)
    await message.answer("Принято!")
```

Объяви `background: BackgroundTasks` как параметр — FastVK инжектирует его автоматически. Вызови `background.add_task(func, *args, **kwargs)` до возврата из хендлера. Все задачи запускаются после завершения хендлера.

## Несколько задач

```python
@router.message()
async def handler(message: Message, background: BackgroundTasks) -> None:
    background.add_task(log_message, message)
    background.add_task(update_stats, message.from_id)
    background.add_task(notify_admin, message.text)
    await message.answer("Обрабатываю!")
```

Задачи выполняются в порядке добавления.

## Синхронные функции

```python
def sync_log(user_id: int) -> None:
    print(f"пользователь {user_id} написал сообщение")

@router.message()
async def handler(message: Message, background: BackgroundTasks) -> None:
    background.add_task(sync_log, message.from_id)
    await message.answer("OK")
```

Поддерживаются и sync, и async функции.

## Передача в другие функции

```python
async def process(message: Message, background: BackgroundTasks) -> None:
    background.add_task(log_message, message)

@router.message()
async def handler(message: Message, background: BackgroundTasks) -> None:
    await process(message, background)
    await message.answer("Готово")
```

Передавай `BackgroundTasks` как обычный аргумент во вспомогательные функции.

## Ошибки в фоновых задачах

Если фоновая задача выбросит исключение — оно логируется (логгер `fastvk.background`), остальные задачи продолжают выполняться.

```python
import logging
logging.getLogger("fastvk.background").setLevel(logging.ERROR)
```
