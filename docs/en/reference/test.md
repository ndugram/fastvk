# Testing utilities

```python
from fastvk.test import MockedBot, message_update, callback_update, dispatch
```

## MockedBot

`Bot` subclass with no network. Records calls, returns canned results.

| Member | Description |
|---|---|
| `MockedBot(token="test-token")` | Construct |
| `set_result(method: str, value)` | Set the return value for a VK method (callable values are invoked) |
| `calls` | `list[Call]` — every call, in order; `Call.method`, `Call.params` |
| `sent_messages` | `list[dict]` — params of each `messages.send` |
| `assert_called(method)` | Return the last matching `Call`, else raise `AssertionError` |
| `assert_not_called(method)` | Raise if the method was called |

Default canned results: `users.get` → one fake user, `messages.send` /
`messages.edit` / `messages.sendMessageEventAnswer` → `1`.

## Update factories

```python
message_update(
    text="", *, from_id=1, peer_id=1, msg_id=1,
    attachments=None, payload=None, group_id=1, event_id=None,
) -> Update

callback_update(
    payload="{}", *, user_id=1, peer_id=1, cmid=1, group_id=1, event_id="evt-cb",
) -> Update
```

## dispatch

```python
async def dispatch(
    router: Router,
    bot: Bot,
    update: Update,
    *,
    storage: BaseStorage | None = None,   # default: fresh MemoryStorage
    data: dict | None = None,             # injected into handlers by type
) -> bool
```

Feeds `update` through `router` and returns whether a handler ran.
