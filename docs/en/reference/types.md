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

## GroupJoinEvent

Typed object injected into handlers registered with `@router.group_join()`.

```python
from fastvk.types import GroupJoinEvent
```

| Field | Type | Description |
|---|---|---|
| `user_id` | `int` | ID of the user who joined |
| `join_type` | `str` | `"join"`, `"invite"`, `"request"`, `"approved"`, `"link"`, `"unsure"`, `"accepted"` |

```python
@bot.group_join()
async def on_join(event: GroupJoinEvent, user: User) -> None:
    print(event.join_type)  # "invite"
```

## GroupLeaveEvent

Typed object injected into handlers registered with `@router.group_leave()`.

```python
from fastvk.types import GroupLeaveEvent
```

| Field | Type | Description |
|---|---|---|
| `user_id` | `int` | ID of the user who left |
| `is_self` | `bool` | `True` — left on their own; `False` — was kicked |

```python
@bot.group_leave()
async def on_leave(event: GroupLeaveEvent) -> None:
    action = "left" if event.is_self else "was kicked"
    print(f"User {event.user_id} {action}.")
```

## WallPostEvent

Typed object injected into handlers registered with `@router.wall_post_new()`.

```python
from fastvk.types import WallPostEvent
```

| Field | Type | Description |
|---|---|---|
| `id` | `int` | Post ID |
| `owner_id` | `int` | Owner ID (negative = community) |
| `from_id` | `int` | Author ID |
| `date` | `int` | Unix timestamp |
| `text` | `str` | Post text |
| `post_type` | `str` | `"post"`, `"copy"`, `"reply"`, `"postpone"`, `"suggest"` |
| `attachments` | `list[dict]` | Raw attachment dicts |
| `raw` | `dict` | Full original object |

```python
@bot.wall_post_new()
async def on_post(event: WallPostEvent, user: User | None = None) -> None:
    author = user.full_name if user else f"id{event.from_id}"
    print(f"New post #{event.id} by {author}: {event.text[:80]!r}")
```

!!! note "User injection"
    `User` is injected automatically for `group_join` and `group_leave` (always positive `user_id`).
    For `wall_post_new` it is injected only when `from_id > 0` (real user, not community).

## Update

Internal type passed to the dispatcher.

```python
from fastvk.types import Update

update.type    # str — "message_new", "message_event", etc.
update.object  # dict — raw event data
```
