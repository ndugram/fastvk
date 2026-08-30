# Testing

`fastvk.test` lets you exercise handlers without a token or network.

```python
from fastvk.test import MockedBot, message_update, callback_update, dispatch
```

## MockedBot

A `Bot` subclass that records every API call and returns canned responses.

```python
import pytest
from fastvk import Router
from fastvk.filters import Command
from fastvk.types import Message
from fastvk.test import MockedBot, dispatch, message_update

router = Router()


@router.message(Command("ping"))
async def ping(message: Message) -> None:
    await message.answer("pong")


@pytest.mark.asyncio
async def test_ping() -> None:
    bot = MockedBot()
    handled = await dispatch(router, bot, message_update("/ping"))

    assert handled is True
    assert bot.sent_messages[0]["message"] == "pong"
    bot.assert_called("messages.send")
```

### Canned responses

```python
bot = MockedBot()
bot.set_result("users.get", [{"id": 7, "first_name": "Ann", "last_name": "Lee"}])
bot.set_result("messages.send", 4242)
```

### Inspecting calls

| Attribute / method | Description |
|---|---|
| `bot.calls` | Every recorded `Call(method, params)` in order |
| `bot.sent_messages` | `params` of every `messages.send` call |
| `bot.assert_called("messages.send")` | Returns the last matching call or raises |
| `bot.assert_not_called("messages.edit")` | Raises if it was called |

## Update factories

```python
message_update("/start", from_id=10, peer_id=2000000001)
message_update("photo", attachments=[{"type": "photo", "photo": {"owner_id": 1, "id": 2}}])
callback_update('{"action": "buy"}', user_id=10)
```

## dispatch()

```python
await dispatch(router, bot, update, storage=MemoryStorage(), data={MyDep: dep})
```

Returns `True` if a handler ran. `storage` and `data` are optional — `data`
values are injected into handlers by type, just like a middleware would.
