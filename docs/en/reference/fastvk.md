# fastvk

Top-level package exports. Everything you need for basic usage can be imported from `fastvk` directly.

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

`FastVK` is a subclass of `Bot` with convenience `run_polling()`.

```python
class FastVK(Bot):
    def __init__(
        self,
        token: str,
        group_id: int,
        *,
        storage: BaseStorage | None = None,
        lifespan: AsyncContextManager | None = None,
        dashboard: BaseDashboard | None = None,
    ) -> None: ...

    def run_polling(self) -> None:
        """Blocking. Runs asyncio.run internally."""
```

## DashboardConfig

Dataclass holding dashboard server settings.

```python
@dataclass
class DashboardConfig:
    dashboard: bool = True          # enable/disable
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = 8080
```

## BaseDashboard

Base class for dashboard configuration. Subclass and override `config`.

```python
class BaseDashboard:
    config: DashboardConfig = DashboardConfig()
```

**Usage:**

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

Pass `dashboard=None` (default) to disable the dashboard entirely.

## Bot

```python
class Bot(Router):
    token: str
    group_id: int

    async def start_polling(self, *, skip_updates: bool = False) -> None: ...
    async def stop(self) -> None: ...

    async def get_me(self) -> Group: ...
    async def get_user(self, user_id: int, fields: str = "") -> User: ...

    # method namespaces
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

Magic filter object. See [Filters](filters.md).

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
    """Matches /start"""

class CommandHelp(Command):
    """Matches /help"""
```
