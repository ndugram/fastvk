# Uploader

```python
from fastvk import Uploader
```

Module for uploading media files (photos, documents, audio messages, graffiti) to VK messages.

## Initialization

```python
from fastvk import FastVK, Uploader

bot = FastVK(token="vk1.a.YOUR_TOKEN")
uploader = Uploader(bot.bot)
```

## Methods

### photo

```python
async def photo(
    peer_id: int,
    file: str | Path | BinaryIO,
    filename: str | None = None,
) -> str
```

Uploads a photo for sending in messages.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `peer_id` | `int` | Destination peer ID (user or chat) |
| `file` | `str | Path | BinaryIO` | Path to image file or file-like object |
| `filename` | `str | None` | Filename (required for file-like objects) |

**Returns:**

- `str` — attachment string like `photo123456_789012`

### document

```python
async def document(
    peer_id: int,
    file: str | Path | BinaryIO,
    filename: str | None = None,
    title: str | None = None,
    tags: str | None = None,
) -> str
```

Uploads a document for sending in messages.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `peer_id` | `int` | Destination peer ID |
| `file` | `str | Path | BinaryIO` | Path to file or file-like object |
| `filename` | `str | None` | Filename (required for file-like objects) |
| `title` | `str | None` | Document title (visible to user) |
| `tags` | `str | None` | Space-separated tags for search |

**Returns:**

- `str` — attachment string like `doc123456_789012`

### audio_message

```python
async def audio_message(
    peer_id: int,
    file: str | Path | BinaryIO,
    filename: str | None = None,
) -> str
```

Uploads an audio message (voice message) for sending in messages.

VK accepts OGG format with Opus codec. For best compatibility, ensure your audio file is encoded as OGG/Opus.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `peer_id` | `int` | Destination peer ID |
| `file` | `str | Path | BinaryIO` | Path to audio file (OGG/Opus recommended) or file-like object |
| `filename` | `str | None` | Filename (required for file-like objects) |

**Returns:**

- `str` — attachment string like `doc123456_789012`

### graffiti

```python
async def graffiti(
    peer_id: int,
    file: str | Path | BinaryIO,
    filename: str | None = None,
) -> str
```

Uploads a graffiti (drawing) for sending in messages.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `peer_id` | `int` | Destination peer ID |
| `file` | `str | Path | BinaryIO` | Path to PNG file with transparent background or file-like object |
| `filename` | `str | None` | Filename (required for file-like objects) |

**Returns:**

- `str` — attachment string like `doc123456_789012`

## Usage

### Upload Photo

```python
@bot.message(Command("photo"))
async def send_photo(message: Message):
    attachment = await uploader.photo(
        peer_id=message.peer_id,
        file="photo.jpg"
    )
    await message.answer_photo(attachment, caption="Here's your photo!")
```

### Upload Document

```python
@bot.message(Command("doc"))
async def send_document(message: Message):
    attachment = await uploader.document(
        peer_id=message.peer_id,
        file="report.pdf",
        title="Q1 Report"
    )
    await message.answer_doc(attachment, caption="Document uploaded")
```

### Audio Message

```python
@bot.message(Command("voice"))
async def send_voice(message: Message):
    attachment = await uploader.audio_message(
        peer_id=message.peer_id,
        file="voice.ogg"
    )
    await message.answer_doc(attachment)
```

### Upload from Memory

```python
import io

@bot.message(Command("memory"))
async def from_memory(message: Message):
    # Create file in memory
    content = b"Hello from FastVK!"
    file_obj = io.BytesIO(content)
    
    attachment = await uploader.document(
        peer_id=message.peer_id,
        file=file_obj,
        filename="hello.txt",
        title="Greeting"
    )
    await message.answer_doc(attachment)
```

### Multiple Attachments

```python
@bot.message(Command("multi"))
async def multiple_files(message: Message):
    photo1 = await uploader.photo(message.peer_id, "photo1.jpg")
    photo2 = await uploader.photo(message.peer_id, "photo2.jpg")
    doc = await uploader.document(message.peer_id, "file.pdf")
    
    # Combine with comma
    attachments = f"{photo1},{photo2},{doc}"
    
    await bot.bot.messages.send(
        peer_id=message.peer_id,
        message="Multiple files:",
        attachment=attachments,
        random_id=0
    )
```

## Error Handling

```python
try:
    attachment = await uploader.photo(
        peer_id=message.peer_id,
        file="photo.jpg"
    )
    await message.answer_photo(attachment)
except FileNotFoundError:
    await message.answer("File not found!")
except ValueError as e:
    await message.answer(f"Parameter error: {e}")
except RuntimeError as e:
    await message.answer(f"Upload error: {e}")
```

## Notes

- **Audio format**: VK requires OGG/Opus format for audio messages. Convert using FFmpeg:
  ```bash
  ffmpeg -i input.mp3 -c:a libopus -b:a 48k output.ogg
  ```

- **File size limits**: VK has file size limits for each attachment type. Check VK API documentation for current limits.

- **Rate limiting**: Uploading many files in quick succession may trigger VK rate limits. Consider adding delays between uploads when necessary.
