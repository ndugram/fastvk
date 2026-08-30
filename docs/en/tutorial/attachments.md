# Attachments

Incoming messages carry attachments as raw dicts in `message.attachments`.
FastVK also parses them into **typed models**, so you get autocomplete and
helpers instead of dictionary digging.

## Content type

```python
@bot.message()
async def any_message(message: Message) -> None:
    print(message.content_type)    # "text", "photo", "audio_message", ...
    print(message.content_types)   # {"text", "photo"} — everything present
```

## Filtering by content type

```python
from fastvk.filters import ContentType, HasAttachment

@bot.message(ContentType("photo"))
async def on_photo(message: Message) -> None:
    await message.answer("Nice photo!")

@bot.message(ContentType("audio_message", "doc"))
async def on_media(message: Message) -> None:
    ...

# any attachment at all
@bot.message(HasAttachment())
async def has_something(message: Message) -> None:
    ...

# any of the given types
@bot.message(HasAttachment("video", "wall"))
async def video_or_repost(message: Message) -> None:
    ...
```

Pass `"text"` to `ContentType` to match plain-text messages.

## Typed accessors

```python
@bot.message(ContentType("photo"))
async def on_photo(message: Message) -> None:
    photo = message.photos[0]
    await message.answer(f"{photo.largest.width}×{photo.largest.height}\n{photo.url}")
```

| Accessor | Returns |
|---|---|
| `message.typed_attachments` | `list` of typed models (`dict` for unknown types) |
| `message.photos` | `list[Photo]` |
| `message.docs` | `list[Document]` |
| `message.videos` | `list[Video]` |
| `message.audio_messages` | `list[AudioMessage]` |
| `message.sticker` | `Sticker | None` |

### Photo

```python
photo.attachment_string   # "photo-1_2" — ready for the attachment= param
photo.sizes               # list[PhotoSize]
photo.largest             # PhotoSize with the most pixels (or None)
photo.url                 # URL of the largest size
```

All models expose `attachment_string` (e.g. `doc-1_2_abcdef`), the fields VK
returns, plus `raw` with the untouched dict.

Available models (import from `fastvk.types`): `Photo`, `Video`, `Audio`,
`Document`, `AudioMessage`, `Sticker`, `Graffiti`, `Link`, `Poll`, `WallPost`.

## Sending several attachments

```python
await message.answer_media_group(["photo1_2", "doc1_3"], caption="Files")
```
