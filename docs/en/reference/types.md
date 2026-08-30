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
message.from_user   # User | None — None until resolved (see get_user / user: User DI)

# typed attachments
message.typed_attachments   # list of typed models (dict for unknown types)
message.content_type        # "text" / "photo" / "audio_message" / ...
message.content_types       # set[str] of everything present
message.has_attachment("photo", "doc")  # bool
message.photos              # list[Photo]
message.docs                # list[Document]
message.videos              # list[Video]
message.audio_messages      # list[AudioMessage]
message.sticker             # Sticker | None
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
await message.answer_media_group(attachments: list[str], caption="", *, keyboard=None) -> int
await message.answer_carousel(carousel, text="") -> int
await message.get_user(fields="") -> User        # fetch + cache the sender

# conversation helpers (uses message.peer_id)
await message.search(q, *, offset=0, count=20, date=None, fields=None) -> dict
await message.get_history(*, offset=0, count=20, start_message_id=None, rev=0, fields=None) -> dict
await message.get_invite_link(*, reset=False) -> str
await message.get_conversation_members(*, fields=None) -> dict

# message helpers
await message.mark_as_important(*, important=True) -> int
await message.restore() -> int
await message.get_by_conversation_message_id(*, fields=None) -> dict
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
callback.from_user  # User | None — None until resolved (declare user: User)
```

### Methods

```python
await callback.answer(text="", *, link=None, app_hash=None) -> None
await callback.edit_message(text, *, keyboard=None, attachment=None) -> int
```

`answer()` shows a snackbar, or opens a link (`link=`) / community app
(`app_hash=`). `edit_message()` edits the message the button belongs to, by
its `conversation_message_id`.

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

## Attachments

Typed models parsed from `message.attachments`. Import from `fastvk.types`.

| Model | `type` | Notable fields |
|---|---|---|
| `Photo` | `photo` | `sizes: list[PhotoSize]`, `largest`, `url`, `text` |
| `Video` | `video` | `title`, `description`, `duration` |
| `Audio` | `audio` | `artist`, `title`, `duration`, `url` |
| `Document` | `doc` | `title`, `size`, `ext`, `url` |
| `AudioMessage` | `audio_message` | `duration`, `link_ogg`, `link_mp3`, `transcript` |
| `Sticker` | `sticker` | `sticker_id`, `product_id` |
| `Graffiti` | `graffiti` | `url`, `width`, `height` |
| `Link` | `link` | `url`, `title`, `description` |
| `Poll` | `poll` | `question`, `votes`, `anonymous`, `multiple` |
| `WallPost` | `wall` | `from_id`, `to_id`, `text` |

Every model (except `Sticker`/`Link`) exposes `attachment_string`
(`"photo-1_2"` / `"doc-1_2_key"`) and `raw` (the untouched dict).

```python
from fastvk.types import parse_attachment, parse_attachments

photo = parse_attachment(message.attachments[0])   # one dict -> model
models = parse_attachments(message.attachments)    # list -> list
```

## Update

Internal type passed to the dispatcher.

```python
from fastvk.types import Update

update.type    # str — "message_new", "message_event", etc.
update.object  # dict — raw event data
```
