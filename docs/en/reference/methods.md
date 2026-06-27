# Methods

Typed VK API method wrappers. All live in `fastvk.methods` and register in the global `_REGISTRY`.

## messages

### messages.send

```python
await bot.messages.send(
    peer_id: int,
    message: str,
    *,
    random_id: int = 0,
    keyboard: str | None = None,
    attachment: str | None = None,
    reply_to: int | None = None,
    sticker_id: int | None = None,
    forward_messages: int | str | None = None,
    payload: str | None = None,
    content_source: str | None = None,
    intent: str | None = None,
    subscribe_id: int | None = None,
) -> int
```

### messages.edit

```python
await bot.messages.edit(
    peer_id: int,
    message_id: int,
    message: str,
    *,
    keyboard: str | None = None,
    attachment: str | None = None,
    content_source: str | None = None,
    template: str | None = None,
    keep_forward_messages: bool = False,
    keep_snippets: bool = False,
) -> int
```

### messages.delete

```python
await bot.messages.delete(
    message_ids: int | str,
    *,
    peer_id: int | None = None,
    cmids: int | str | None = None,
    delete_for_all: bool = False,
    spam: bool = False,
) -> dict
```

### messages.restore

```python
await bot.messages.restore(message_id: int) -> int
```

### messages.pin

```python
await bot.messages.pin(
    peer_id: int,
    *,
    message_id: int | None = None,
    conversation_message_id: int | None = None,
) -> dict
```

### messages.unpin

```python
await bot.messages.unpin(peer_id: int) -> int
```

### messages.mark_as_read

```python
await bot.messages.mark_as_read(
    peer_id: int | None = None,
    *,
    message_ids: str | None = None,
    start_message_id: int | None = None,
) -> int
```

### messages.get_by_id

```python
await bot.messages.get_by_id(
    message_ids: int | str,
    *,
    fields: str | None = None,
    preview_length: int | None = None,
) -> dict
```

### messages.get_by_conversation_message_id

```python
await bot.messages.get_by_conversation_message_id(
    peer_id: int,
    conversation_message_ids: list[int],
    *,
    fields: str | None = None,
) -> dict
```

### messages.get_history

```python
await bot.messages.get_history(
    peer_id: int,
    *,
    offset: int = 0,
    count: int = 20,
    start_message_id: int | None = None,
    rev: int = 0,
    fields: str | None = None,
) -> dict
```

### messages.search

```python
await bot.messages.search(
    q: str,
    *,
    peer_id: int | None = None,
    offset: int = 0,
    count: int = 20,
    date: int | None = None,
    fields: str | None = None,
) -> dict
```

### messages.get_history_attachments

```python
await bot.messages.get_history_attachments(
    peer_id: int,
    *,
    media_type: str | None = None,
    start_from: str | None = None,
    count: int = 20,
    fields: str | None = None,
) -> dict
```

### messages.get_conversations

```python
await bot.messages.get_conversations(
    *,
    offset: int = 0,
    count: int = 20,
    filter: str = "all",
    fields: str | None = None,
) -> dict
```

### messages.search_conversations

```python
await bot.messages.search_conversations(
    q: str,
    *,
    count: int = 20,
    fields: str | None = None,
) -> dict
```

### messages.get_conversation_members

```python
await bot.messages.get_conversation_members(
    peer_id: int,
    *,
    fields: str | None = None,
) -> dict
```

### messages.get_peers_subscriptions

```python
await bot.messages.get_peers_subscriptions(
    *,
    peer_ids: list[int] | None = None,
) -> dict
```

### messages.get_last_activity

```python
await bot.messages.get_last_activity(user_id: int) -> dict
```

### messages.create_chat

```python
await bot.messages.create_chat(
    title: str,
    *,
    peer_ids: list[int] | None = None,
) -> int
```

### messages.edit_chat

```python
await bot.messages.edit_chat(chat_id: int, title: str) -> int
```

### messages.get_chat

```python
await bot.messages.get_chat(
    chat_id: int,
    *,
    fields: str | None = None,
) -> dict
```

### messages.add_chat_user

```python
await bot.messages.add_chat_user(
    chat_id: int,
    user_id: int,
    *,
    visible_messages_count: int = 0,
) -> int
```

### messages.remove_chat_user

```python
await bot.messages.remove_chat_user(
    chat_id: int,
    user_id: int,
) -> int
```

### messages.get_invite_link

```python
await bot.messages.get_invite_link(
    peer_id: int,
    *,
    reset: bool = False,
) -> str
```

### messages.join_chat_by_invite_link

```python
await bot.messages.join_chat_by_invite_link(link: str) -> dict
```

### messages.get_chat_preview

```python
await bot.messages.get_chat_preview(
    link: str,
    *,
    fields: str | None = None,
) -> dict
```

### messages.set_chat_photo

```python
await bot.messages.set_chat_photo(file: str) -> dict
```

### messages.delete_chat_photo

```python
await bot.messages.delete_chat_photo(chat_id: int) -> dict
```

### messages.set_activity

```python
await bot.messages.set_activity(
    peer_id: int,
    *,
    type: str = "typing",
) -> int
```

### messages.send_event_answer

```python
await bot.messages.send_event_answer(
    event_id: str,
    user_id: int,
    peer_id: int,
    *,
    event_data: str | None = None,
) -> int
```

### messages.allow_messages_from_group

```python
await bot.messages.allow_messages_from_group(
    group_id: int,
    *,
    key: str | None = None,
) -> int
```

### messages.deny_messages_from_group

```python
await bot.messages.deny_messages_from_group(group_id: int) -> int
```

### messages.mark_as_important

```python
await bot.messages.mark_as_important(
    message_ids: int | str,
    *,
    important: bool = True,
) -> int
```

### messages.get_important_messages

```python
await bot.messages.get_important_messages(
    *,
    offset: int = 0,
    count: int = 20,
    fields: str | None = None,
) -> dict
```

### messages.delete_conversation

```python
await bot.messages.delete_conversation(peer_id: int) -> int
```

### messages.get_long_poll_history

```python
await bot.messages.get_long_poll_history(
    ts: int,
    *,
    pts: int | None = None,
    fields: str | None = None,
) -> dict
```

## users

### users.get

```python
await bot.users.get(
    user_ids: int | str | list,
    *,
    fields: str = "",
) -> list[dict]
```

## groups

### groups.get_by_id

```python
await bot.groups.get_by_id(
    *,
    fields: str = "",
) -> list[dict]
```

## wall

### wall.get

```python
await bot.wall.get(
    owner_id: int,
    *,
    count: int = 20,
    offset: int = 0,
    filter: str | None = None,
    extended: bool = False,
) -> dict   # {"count": int, "items": list[dict]}
```

Paginated wall feed. Best used with `bot.collect()`:

```python
from fastvk.methods import WallGet

posts = await bot.collect(WallGet, owner_id=-123, count=100)
```

### wall.post

```python
await bot.wall.post(
    owner_id: int,
    message: str,
    *,
    attachments: str | None = None,
) -> dict   # {"post_id": int}
```

### wall.get_by_id

```python
await bot.wall.get_by_id(posts: str) -> list[dict]
```

`posts` format: `"{owner_id}_{post_id}"` or comma-separated list.

## photos

### photos.get_messages_upload_server

```python
await bot.photos.get_messages_upload_server(peer_id: int) -> dict
# {"upload_url": str, "album_id": int, "user_id": int}
```

### photos.save_messages_photo

```python
await bot.photos.save_messages_photo(
    photo: str,
    server: int,
    hash: str,
) -> list[dict]
```

## docs

### docs.get_messages_upload_server

```python
await bot.docs.get_messages_upload_server(
    peer_id: int,
    *,
    type: str = "doc",
) -> dict   # {"upload_url": str}
```

### docs.save

```python
await bot.docs.save(
    file: str,
    *,
    title: str = "",
    tags: str = "",
) -> dict
```
