# Scheduler

```python
from fastvk import Scheduler
```

Внутрипроцессный планировщик по интервалу / времени суток, работающий в цикле
событий бота.

## Декораторы

### @scheduler.every

```python
@scheduler.every(interval: float | str, *, name: str | None = None)
async def job() -> None: ...
```

Повторяющийся запуск. `interval` — секунды или строка: `"45s"`, `"5m"`, `"2h"`, `"1d"`.

### @scheduler.at

```python
@scheduler.at("ЧЧ:ММ", *, name: str | None = None)
async def job() -> None: ...
```

Запуск раз в сутки в указанное локальное время.

## Методы

| Метод | Описание |
|---|---|
| `add_job(func, interval, *args, name=None, **kwargs)` | Зарегистрировать задачу вручную |
| `bind(*objects)` | Зарегистрировать объекты, инжектируемые в задачи по типу |
| `await start()` | Запустить цикл планировщика (идемпотентно) |
| `await stop()` | Остановить цикл |

## Внедрение зависимостей

Задача с типизированными параметрами получает любой объект, переданный в
`scheduler.bind(...)`, чей тип совпадает. Задачи, созданные с аргументами
через `add_job`, не инжектируются.

```python
scheduler.bind(bot)

@scheduler.every("30m")
async def refresh(bot: FastVK) -> None:
    ...
```

## Подключение к боту

```python
@bot.startup
async def _start(bot: FastVK) -> None:
    scheduler.bind(bot)
    await scheduler.start()

@bot.shutdown
async def _stop() -> None:
    await scheduler.stop()
```

Исключения задач логируются (`fastvk.scheduler`) и не останавливают цикл.
Точность таймингов — около 1 секунды.
