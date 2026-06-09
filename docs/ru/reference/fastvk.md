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
        group_id: int,
        *,
        storage: BaseStorage | None = None,
        lifespan: AsyncContextManager | None = None,
        api_version: str = "5.199",
    ) -> None: ...

    def run_polling(self, *, skip_updates: bool = False) -> None:
        """Блокирующий. Запускает asyncio.run(self.start_polling(...))."""
```

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
