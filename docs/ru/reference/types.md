# Типы

Все типы — подклассы Pydantic v2 `BaseModel`.

## Message

```python
from fastvk.types import Message
```

| Поле | Тип | Описание |
|---|---|---|
| `id` | `int` | ID сообщения |
| `date` | `int` | Unix timestamp |
| `peer_id` | `int` | ID беседы/чата |
| `from_id` | `int` | ID отправителя |
| `text` | `str` | Текст сообщения |
| `attachments` | `list[dict]` | Сырые словари вложений |
| `payload` | `str \| None` | Payload кнопки клавиатуры |

### Вычисляемые свойства

```python
message.is_private  # bool — peer_id == from_id
message.is_chat     # bool — peer_id > 2_000_000_000
message.chat_id     # int | None — peer_id - 2_000_000_000 (только чаты)
message.from_user   # User | None — получен автоматически
```

### Методы

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

# вспомогательные методы чата (используют message.peer_id)
await message.search(q, *, offset=0, count=20, date=None, fields=None) -> dict
await message.get_history(*, offset=0, count=20, start_message_id=None, rev=0, fields=None) -> dict
await message.get_invite_link(*, reset=False) -> str
await message.get_conversation_members(*, fields=None) -> dict

# вспомогательные методы сообщения
await message.mark_as_important(*, important=True) -> int
await message.restore() -> int
await message.get_by_conversation_message_id(*, fields=None) -> dict
```

## User

```python
from fastvk.types import User
```

| Поле | Тип | Описание |
|---|---|---|
| `id` | `int` | ID пользователя |
| `first_name` | `str` | Имя |
| `last_name` | `str` | Фамилия |
| `screen_name` | `str \| None` | `@username` |
| `photo_200` | `str \| None` | URL аватара |

## Group

```python
from fastvk.types import Group
```

| Поле | Тип | Описание |
|---|---|---|
| `id` | `int` | ID группы/сообщества |
| `name` | `str` | Название сообщества |
| `screen_name` | `str \| None` | `@slug` |
| `description` | `str \| None` | Описание |
| `members_count` | `int \| None` | Количество участников |

## CallbackQuery

```python
from fastvk.types import CallbackQuery
```

| Поле | Тип | Описание |
|---|---|---|
| `user_id` | `int` | Пользователь нажавший кнопку |
| `peer_id` | `int` | ID беседы |
| `event_id` | `str` | Уникальный ID события |
| `payload` | `dict` | Словарь payload кнопки |

### Свойства

```python
callback.from_user  # User | None — автоматически получен из VK API
```

### Методы

```python
await callback.answer(text=None, *, event_data=None) -> None
```

Отправляет snackbar уведомление пользователю (или очищает его если `text=None`).

## GroupJoinEvent

Типизированный объект, внедряемый в хендлеры `@router.group_join()`.

```python
from fastvk.types import GroupJoinEvent
```

| Поле | Тип | Описание |
|---|---|---|
| `user_id` | `int` | ID пользователя, вступившего в группу |
| `join_type` | `str` | `"join"`, `"invite"`, `"request"`, `"approved"`, `"link"`, `"unsure"`, `"accepted"` |

```python
@bot.group_join()
async def on_join(event: GroupJoinEvent, user: User) -> None:
    print(event.join_type)  # "invite"
```

## GroupLeaveEvent

Типизированный объект, внедряемый в хендлеры `@router.group_leave()`.

```python
from fastvk.types import GroupLeaveEvent
```

| Поле | Тип | Описание |
|---|---|---|
| `user_id` | `int` | ID пользователя, покинувшего группу |
| `is_self` | `bool` | `True` — вышел сам; `False` — был исключён |

```python
@bot.group_leave()
async def on_leave(event: GroupLeaveEvent) -> None:
    action = "сам покинул" if event.is_self else "был исключён из"
    print(f"Пользователь {event.user_id} {action} группы.")
```

## WallPostEvent

Типизированный объект, внедряемый в хендлеры `@router.wall_post_new()`.

```python
from fastvk.types import WallPostEvent
```

| Поле | Тип | Описание |
|---|---|---|
| `id` | `int` | ID поста |
| `owner_id` | `int` | ID владельца (отрицательный = сообщество) |
| `from_id` | `int` | ID автора |
| `date` | `int` | Unix timestamp |
| `text` | `str` | Текст поста |
| `post_type` | `str` | `"post"`, `"copy"`, `"reply"`, `"postpone"`, `"suggest"` |
| `attachments` | `list[dict]` | Сырые словари вложений |
| `raw` | `dict` | Полный оригинальный объект |

```python
@bot.wall_post_new()
async def on_post(event: WallPostEvent, user: User | None = None) -> None:
    author = user.full_name if user else f"id{event.from_id}"
    print(f"Новый пост #{event.id} от {author}: {event.text[:80]!r}")
```

!!! note "Внедрение User"
    `User` автоматически внедряется для `group_join` и `group_leave` (всегда положительный `user_id`).
    Для `wall_post_new` — только когда `from_id > 0` (реальный пользователь, не сообщество).

## Update

Внутренний тип передаваемый диспетчеру.

```python
from fastvk.types import Update

update.type    # str — "message_new", "message_event", и т.д.
update.object  # dict — сырые данные события
```
