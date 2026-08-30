# Bot

`Bot` is the core class. `FastVK` extends it with `run_polling()`.

## Constructor

```python
Bot(
    token: str,
    group_id: int,
    *,
    storage: BaseStorage | None = None,
    lifespan: AsyncContextManager | None = None,
    api_version: str = "5.199",
)
```

| Parameter | Type | Description |
|---|---|---|
| `token` | `str` | VK community token |
| `group_id` | `int` | VK community ID |
| `storage` | `BaseStorage` | FSM storage. Default: `MemoryStorage()` |
| `lifespan` | async context manager | Startup/shutdown hook |
| `api_version` | `str` | VK API version. Default: `"5.199"` |
| `timeout` | `float` | Per-request HTTP timeout in seconds. Default: `30.0` |
| `max_retries` | `int` | Retries for network errors and codes 1/6/9/10/29. Default: `3` |
| `captcha_handler` | `async (sid, img_url) -> answer` | Solver invoked on error code 14 |
| `max_concurrency` | `int` | `FastVK` only — cap on updates processed in parallel (`0` = unbounded) |
| `polling` | `"group"` \| `"user"` | `FastVK` only — long-poll flavour. Default: `"group"` |

## Methods

### start_polling

```python
async def start_polling(self, *, skip_updates: bool = False) -> None
```

Start long-polling loop. Blocks until `stop()` is called or process interrupted.

- `skip_updates=True` — discard queued updates before starting.

### stop

```python
async def stop(self) -> None
```

Gracefully stop the polling loop.

### get_me

```python
async def get_me(self) -> Group
```

Return info about the bot's community (calls `groups.getById`).

### collect

```python
async def collect(
    method_class: type[VKMethod],
    *,
    max_total: int = 0,
    items_key: str | None = None,
    count: int = 100,
    offset: int = 0,
    **kwargs,
) -> list[Any]
```

Automatically iterate over all pages of a paginated VK API method.

Accepts a typed method class — full IDE autocomplete.

```python
from fastvk.methods import GroupsGetMembers, WallGet, MessagesGetHistory

# All group members (auto-paginated)
members = await bot.collect(GroupsGetMembers, group_id=123, fields="photo_200")

# Recent posts (max 500)
posts = await bot.collect(WallGet, owner_id=-123, count=100, max_total=500)

# Chat history
history = await bot.collect(MessagesGetHistory, peer_id=2000000001)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `method_class` | — | Typed VK method class (e.g. `GroupsGetMembers`) |
| `max_total` | `0` | Limit total items (`0` = unlimited) |
| `items_key` | auto | Response key with item list (auto-detected) |
| `count` | `100` | Items per page |
| `offset` | `0` | Starting offset |

### get_user

```python
async def get_user(self, user_id: int, fields: str = "") -> User
```

Return user info (calls `users.get`).

```python
user = await bot.get_user(123456)
user = await bot.get_user(123456, fields="photo_200,city")
```

### execute / execute_batch

```python
async def execute(self, code: str) -> Any
async def execute_batch(self, calls: list[tuple[str, dict]]) -> list[Any]
```

`execute()` runs a VKScript snippet server-side. `execute_batch()` packs up to
25 API calls into one request and returns their results in order.

```python
results = await bot.execute_batch([
    ("users.get", {"user_ids": 1}),
    ("groups.getById", {"group_id": 1}),
])
```

### download

```python
async def download(self, url: str, dest: str | Path | None = None) -> bytes
```

Download a file (e.g. an attachment URL). Writes to `dest` if given.

### set_captcha_handler

```python
def set_captcha_handler(self, handler: Callable[[str, str], Awaitable[str]]) -> None
```

Register `(captcha_sid, captcha_img_url) -> answer`. When VK returns error
code 14 the failed call is retried once with the answer.

### _call

```python
async def _call(self, method: str, **params) -> Any
```

Low-level API call. Retries network errors and codes 1/6/9/10/29 with
exponential backoff; raises `VKAPIError` otherwise.

## API namespaces

```python
bot.messages   # MessagesNamespace
bot.users      # UsersNamespace
bot.groups     # GroupsNamespace
bot.wall       # WallNamespace
bot.photos     # PhotosNamespace
bot.docs       # DocsNamespace
```

Each namespace has typed methods that return parsed models. Example:

```python
msg_id = await bot.messages.send(peer_id=123, message="Hi", random_id=0)
# msg_id: int

user_list = await bot.users.get(user_ids=123456)
# user_list: list[dict]
```
