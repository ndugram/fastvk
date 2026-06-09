# Types

All types are Pydantic v2 `BaseModel` subclasses.

## Message

```python
from fastvk.types import Message
```

| Field | Type | Description |
|---|---|---|
| `id` | `int` | Message ID |
| `date` | `int` | Unix timestamp |
| `peer_id` | `int` | Conversation/chat ID |
| `from_id` | `int` | Sender user ID |
| `text` | `str` | Message text |
| `attachments` | `list[dict]` | Raw attachment dicts |
| `payload` | `str \| None` | Keyboard button payload |

### Computed properties

```python
message.is_private  # bool — peer_id == from_id
message.is_chat     # bool — peer_id > 2_000_000_000
message.chat_id     # int | None — peer_id - 2_000_000_000 (chats only)
message.from_user   # User | None — fetched automatically
```

### Methods

```python
await message.answer(text, *, keyboard=None, parse_mode=None, dont_parse_links=False, disable_mentions=False) -> int
await message.reply(text, ...) -> int
await message.edit(text, *, keyboard=None, attachment=None, dont_parse_links=False, disable_mentions=False) -> int
await message.delete(*, delete_for_all=False) -> int
await message.pin() -> dict
await message.unpin() -> int
await message.mark_as_read() -> int
await message.typing(action=ChatAction.TYPING) -> None
await message.forward(peer_id=None) -> int
await message.answer_photo(attachment, *, caption=None, ...) -> int
await message.answer_doc(attachment, *, caption=None, ...) -> int
await message.answer_video(attachment, *, caption=None, ...) -> int
await message.answer_sticker(sticker_id) -> int
```

## User

```python
from fastvk.types import User
```

| Field | Type | Description |
|---|---|---|
| `id` | `int` | User ID |
| `first_name` | `str` | First name |
| `last_name` | `str` | Last name |
| `screen_name` | `str \| None` | `@username` |
| `photo_200` | `str \| None` | Avatar URL |

## Group

```python
from fastvk.types import Group
```

| Field | Type | Description |
|---|---|---|
| `id` | `int` | Group/community ID |
| `name` | `str` | Community name |
| `screen_name` | `str \| None` | `@slug` |
| `description` | `str \| None` | Description |
| `members_count` | `int \| None` | Member count |

## CallbackQuery

```python
from fastvk.types import CallbackQuery
```

| Field | Type | Description |
|---|---|---|
| `user_id` | `int` | User who pressed the button |
| `peer_id` | `int` | Conversation ID |
| `event_id` | `str` | Unique event ID |
| `payload` | `dict` | Button payload dict |

### Properties

```python
callback.from_user  # User | None — auto-fetched from VK API
```

### Methods

```python
await callback.answer(text=None, *, event_data=None) -> None
```

Sends a snackbar notification to the user (or clears it if `text=None`).

## Update

Internal type passed to the dispatcher.

```python
from fastvk.types import Update

update.type    # str — "message_new", "message_event", etc.
update.object  # dict — raw event data
```
