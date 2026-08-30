# Вложения

Во входящих сообщениях вложения лежат сырыми словарями в `message.attachments`.
FastVK также разбирает их в **типизированные модели** — вместо копания в словарях
получаешь автодополнение и хелперы.

## Тип содержимого

```python
@bot.message()
async def any_message(message: Message) -> None:
    print(message.content_type)    # "text", "photo", "audio_message", ...
    print(message.content_types)   # {"text", "photo"} — всё, что присутствует
```

## Фильтрация по типу вложения

```python
from fastvk.filters import ContentType, HasAttachment

@bot.message(ContentType("photo"))
async def on_photo(message: Message) -> None:
    await message.answer("Красивое фото!")

@bot.message(ContentType("audio_message", "doc"))
async def on_media(message: Message) -> None:
    ...

# любое вложение
@bot.message(HasAttachment())
async def has_something(message: Message) -> None:
    ...

# любое из перечисленных
@bot.message(HasAttachment("video", "wall"))
async def video_or_repost(message: Message) -> None:
    ...
```

Передай `"text"` в `ContentType`, чтобы совпадать с текстовыми сообщениями.

## Типизированные аксессоры

```python
@bot.message(ContentType("photo"))
async def on_photo(message: Message) -> None:
    photo = message.photos[0]
    await message.answer(f"{photo.largest.width}×{photo.largest.height}\n{photo.url}")
```

| Аксессор | Возвращает |
|---|---|
| `message.typed_attachments` | `list` типизированных моделей (`dict` для неизвестных типов) |
| `message.photos` | `list[Photo]` |
| `message.docs` | `list[Document]` |
| `message.videos` | `list[Video]` |
| `message.audio_messages` | `list[AudioMessage]` |
| `message.sticker` | `Sticker | None` |

### Photo

```python
photo.attachment_string   # "photo-1_2" — готово для параметра attachment=
photo.sizes               # list[PhotoSize]
photo.largest             # PhotoSize с максимумом пикселей (или None)
photo.url                 # URL самого крупного размера
```

Все модели имеют `attachment_string` (например `doc-1_2_abcdef`), поля,
которые вернул VK, и `raw` с исходным словарём.

Доступные модели (импорт из `fastvk.types`): `Photo`, `Video`, `Audio`,
`Document`, `AudioMessage`, `Sticker`, `Graffiti`, `Link`, `Poll`, `WallPost`.

## Отправка нескольких вложений

```python
await message.answer_media_group(["photo1_2", "doc1_3"], caption="Файлы")
```
