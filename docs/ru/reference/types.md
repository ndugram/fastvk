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

## Update

Внутренний тип передаваемый диспетчеру.

```python
from fastvk.types import Update

update.type    # str — "message_new", "message_event", и т.д.
update.object  # dict — сырые данные события
```
