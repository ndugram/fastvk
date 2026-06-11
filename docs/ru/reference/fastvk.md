# fastvk

Основные экспорты пакета. Всё необходимое для базового использования импортируется прямо из `fastvk`.

```python
from fastvk import (
    FastVK,
    Bot,
    Router,
    F,
    Command,
    CommandStart,
    CommandHelp,
)
```

## FastVK

`FastVK` — подкласс `Bot` с удобным методом `run_polling()`.

```python
class FastVK(Bot):
    def __init__(
        self,
        token: str,
        group_id: int | None = None,
        *,
        storage: BaseStorage | None = None,
        lifespan: AsyncContextManager | None = None,
        dashboard: BaseDashboard | None = None,
        throttle_rate: float = 1.0,
    ) -> None: ...

    def run_polling(self) -> None:
        """Блокирующий. Запускает asyncio.run внутри."""
```

| Параметр | По умолчанию | Описание |
|---|---|---|
| `group_id` | `None` | ID группы. Если не передан — определяется автоматически из токена через `groups.getById` при старте. |
| `throttle_rate` | `1.0` | Минимальный интервал между сообщениями от одного пользователя (секунды). Передай `0` чтобы отключить. |

## ThrottlingMiddleware

Встроенный rate limiter, регистрируется автоматически в `FastVK`. Настраивать ничего не нужно.

```python
# по умолчанию — 1 сообщение в секунду на пользователя
bot = FastVK(token=TOKEN, group_id=GROUP_ID)

# другой rate
bot = FastVK(token=TOKEN, group_id=GROUP_ID, throttle_rate=0.5)

# отключить
bot = FastVK(token=TOKEN, group_id=GROUP_ID, throttle_rate=0)
```

Если пользователь отправляет сообщения быстрее чем `throttle_rate` секунд, лишние обновления молча дропаются — хэндлер не вызывается. Работает для всех типов событий (`message_new`, `message_event`, `group_join`, `group_leave`). Посты сообщества (`wall_post_new` с отрицательным `from_id`) не троттлируются никогда.

Если нужен класс напрямую:

```python
from fastvk.middleware import ThrottlingMiddleware
```

## DashboardConfig

Датакласс с настройками сервера дашборда.

```python
@dataclass
class DashboardConfig:
    dashboard: bool = True          # включить/выключить
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = 8080
```

## BaseDashboard

Базовый класс конфигурации дашборда. Создай подкласс и переопредели `config`.

```python
class BaseDashboard:
    config: DashboardConfig = DashboardConfig()
```

**Использование:**

```python
from fastvk import FastVK
from fastvk.dashboard import BaseDashboard, DashboardConfig

class MyDashboard(BaseDashboard):
    config = DashboardConfig(
        dashboard_host="0.0.0.0",
        dashboard_port=8080,
    )

bot = FastVK(token=TOKEN, group_id=GROUP_ID, dashboard=MyDashboard())
```

`dashboard=None` (по умолчанию) — дашборд отключён.

## Bot

```python
class Bot(Router):
    token: str
    group_id: int

    async def start_polling(self, *, skip_updates: bool = False) -> None: ...
    async def stop(self) -> None: ...

    async def get_me(self) -> Group: ...
    async def get_user(self, user_id: int, fields: str = "") -> User: ...

    # пространства методов
    messages: MessagesNamespace
    users: UsersNamespace
    groups: GroupsNamespace
    wall: WallNamespace
    photos: PhotosNamespace
    docs: DocsNamespace
```

## Router

```python
class Router:
    def message(self, *filters) -> Callable: ...
    def callback(self, *filters) -> Callable: ...
    def error(self) -> Callable: ...
    def include_router(self, router: Router) -> None: ...
```

## F

Magic filter объект. Смотри [Фильтры](filters.md).

```python
F.text == "hello"
F.text.startswith("!")
F.text.regexp(r"\d+")
F.from_id.in_(1, 2, 3)
~F.text.startswith("/")
(F.text == "a") | (F.text == "b")
```

## Command, CommandStart, CommandHelp

```python
class Command:
    def __init__(self, *commands: str, prefix: str = "/") -> None: ...

class CommandStart(Command):
    """Совпадает с /start"""

class CommandHelp(Command):
    """Совпадает с /help"""
```
