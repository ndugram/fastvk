# Методы

Типизированные обёртки VK API методов. Все находятся в `fastvk.methods` и регистрируются в глобальном `_REGISTRY`.

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
    dont_parse_links: bool = False,
    disable_mentions: bool = False,
) -> int   # ID сообщения
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
) -> int
```

### messages.delete

```python
await bot.messages.delete(
    message_ids: int | list[int],
    *,
    peer_id: int | None = None,
    delete_for_all: bool = False,
) -> int
```

### messages.pin

```python
await bot.messages.pin(peer_id: int, message_id: int) -> dict
```

### messages.unpin

```python
await bot.messages.unpin(peer_id: int) -> int
```

### messages.mark_as_read

```python
await bot.messages.mark_as_read(peer_id: int) -> int
```

### messages.get_history

```python
await bot.messages.get_history(
    peer_id: int,
    *,
    count: int = 20,
    offset: int = 0,
) -> dict   # {"count": int, "items": list[dict]}
```

### messages.set_activity

```python
await bot.messages.set_activity(
    peer_id: int,
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

Пагинированная лента записей. Лучше всего использовать с `bot.collect()`:

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

Формат `posts`: `"{owner_id}_{post_id}"` или список через запятую.

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
