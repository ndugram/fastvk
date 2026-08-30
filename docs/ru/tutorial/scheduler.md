# Планировщик

`Scheduler` запускает корутины по интервалу или в фиксированное время суток —
в том же цикле событий, что и бот. Без внешних зависимостей.

```python
from fastvk import FastVK, Scheduler
from fastvk.types import Message

bot = FastVK(token="vk1.a.YOUR_TOKEN")
scheduler = Scheduler()


@scheduler.every("30m")
async def refresh() -> None:
    ...


@scheduler.at("09:00")
async def morning_digest() -> None:
    ...


@bot.startup
async def _start(bot: FastVK) -> None:
    scheduler.bind(bot)          # сделать `bot` инжектируемым в задачи
    await scheduler.start()


@bot.shutdown
async def _stop() -> None:
    await scheduler.stop()


if __name__ == "__main__":
    bot.run_polling()
```

## Интервалы

`every()` принимает число секунд или короткую строку:

| Строка | Значение |
|---|---|
| `"45s"` | 45 секунд |
| `"5m"` | 5 минут |
| `"2h"` | 2 часа |
| `"1d"` | 1 день |

`at("ЧЧ:ММ")` запускает задачу раз в сутки в указанное локальное время.

## Внедрение зависимостей в задачи

`scheduler.bind(obj)` регистрирует объект по его типу. Задача, у которой
объявлен параметр подходящего типа, получит его:

```python
scheduler.bind(bot, db)

@scheduler.every("1h")
async def cleanup(bot: FastVK, db: Database) -> None:
    ...
```

## Императивные задачи

```python
scheduler.add_job(send_report, "12h", chat_id=2000000001, name="report")
```

## API

| Метод | Описание |
|---|---|
| `@scheduler.every(interval, *, name=None)` | Запуск по интервалу |
| `@scheduler.at("ЧЧ:ММ", *, name=None)` | Запуск раз в сутки |
| `scheduler.add_job(func, interval, *args, name=None, **kwargs)` | Регистрация вручную |
| `scheduler.bind(*objects)` | Зарегистрировать инжектируемые объекты по типу |
| `await scheduler.start()` / `await scheduler.stop()` | Управление циклом |
