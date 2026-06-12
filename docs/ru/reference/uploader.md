# Uploader

```python
from fastvk import Uploader
```

Модуль для загрузки медиафайлов (фото, документы, голосовые сообщения, граффити) в сообщения VK.

## Инициализация

```python
from fastvk import FastVK, Uploader

bot = FastVK(token="vk1.a.YOUR_TOKEN")
uploader = Uploader(bot.bot)
```

## Методы

### photo

```python
async def photo(
    peer_id: int,
    file: str | Path | BinaryIO,
    filename: str | None = None,
) -> str
```

Загружает фото для отправки в сообщениях.

**Параметры:**

| Параметр | Тип | Описание |
|---|---|---|
| `peer_id` | `int` | ID получателя (пользователя или беседы) |
| `file` | `str | Path | BinaryIO` | Путь к файлу изображения или file-объект |
| `filename` | `str | None` | Имя файла (обязательно для file-объектов) |

**Возвращает:**

- `str` — строку attachment вида `photo123456_789012`

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

Загружает документ для отправки в сообщениях.

**Параметры:**

| Параметр | Тип | Описание |
|---|---|---|
| `peer_id` | `int` | ID получателя |
| `file` | `str | Path | BinaryIO` | Путь к файлу или file-объект |
| `filename` | `str | None` | Имя файла (обязательно для file-объектов) |
| `title` | `str | None` | Название документа (видно пользователю) |
| `tags` | `str | None` | Теги через пробел для поиска |

**Возвращает:**

- `str` — строку attachment вида `doc123456_789012`

### audio_message

```python
async def audio_message(
    peer_id: int,
    file: str | Path | BinaryIO,
    filename: str | None = None,
) -> str
```

Загружает голосовое сообщение для отправки в сообщениях.

VK принимает формат OGG с кодеком Opus. Для лучшей совместимости используйте аудио в формате OGG/Opus.

**Параметры:**

| Параметр | Тип | Описание |
|---|---|---|
| `peer_id` | `int` | ID получателя |
| `file` | `str | Path | BinaryIO` | Путь к аудиофайлу (рекомендуется OGG/Opus) или file-объект |
| `filename` | `str | None` | Имя файла (обязательно для file-объектов) |

**Возвращает:**

- `str` — строку attachment вида `doc123456_789012`

### graffiti

```python
async def graffiti(
    peer_id: int,
    file: str | Path | BinaryIO,
    filename: str | None = None,
) -> str
```

Загружает граффити (рисунок) для отправки в сообщениях.

**Параметры:**

| Параметр | Тип | Описание |
|---|---|---|
| `peer_id` | `int` | ID получателя |
| `file` | `str | Path | BinaryIO` | Путь к PNG файлу с прозрачным фоном или file-объект |
| `filename` | `str | None` | Имя файла (обязательно для file-объектов) |

**Возвращает:**

- `str` — строку attachment вида `doc123456_789012`

## Использование

### Загрузка фото

```python
@bot.message(Command("photo"))
async def send_photo(message: Message):
    attachment = await uploader.photo(
        peer_id=message.peer_id,
        file="photo.jpg"
    )
    await message.answer_photo(attachment, caption="Вот фото!")
```

### Загрузка документа

```python
@bot.message(Command("doc"))
async def send_document(message: Message):
    attachment = await uploader.document(
        peer_id=message.peer_id,
        file="report.pdf",
        title="Отчёт за Q1"
    )
    await message.answer_doc(attachment, caption="Документ загружен")
```

### Голосовое сообщение

```python
@bot.message(Command("voice"))
async def send_voice(message: Message):
    attachment = await uploader.audio_message(
        peer_id=message.peer_id,
        file="voice.ogg"
    )
    await message.answer_doc(attachment)
```

### Загрузка из памяти

```python
import io

@bot.message(Command("memory"))
async def from_memory(message: Message):
    # Создание файла в памяти
    content = b"Привет из FastVK!"
    file_obj = io.BytesIO(content)
    
    attachment = await uploader.document(
        peer_id=message.peer_id,
        file=file_obj,
        filename="hello.txt",
        title="Приветствие"
    )
    await message.answer_doc(attachment)
```

### Несколько вложений

```python
@bot.message(Command("multi"))
async def multiple_files(message: Message):
    photo1 = await uploader.photo(message.peer_id, "photo1.jpg")
    photo2 = await uploader.photo(message.peer_id, "photo2.jpg")
    doc = await uploader.document(message.peer_id, "file.pdf")
    
    # Объединяем через запятую
    attachments = f"{photo1},{photo2},{doc}"
    
    await bot.bot.messages.send(
        peer_id=message.peer_id,
        message="Несколько файлов:",
        attachment=attachments,
        random_id=0
    )
```

## Обработка ошибок

```python
try:
    attachment = await uploader.photo(
        peer_id=message.peer_id,
        file="photo.jpg"
    )
    await message.answer_photo(attachment)
except FileNotFoundError:
    await message.answer("Файл не найден!")
except ValueError as e:
    await message.answer(f"Ошибка параметров: {e}")
except RuntimeError as e:
    await message.answer(f"Ошибка загрузки: {e}")
```

## Примечания

- **Формат аудио**: VK требует формат OGG/Opus для голосовых сообщений. Конвертация через FFmpeg:
  ```bash
  ffmpeg -i input.mp3 -c:a libopus -b:a 48k output.ogg
  ```

- **Ограничения размера**: VK имеет ограничения на размер файлов для каждого типа вложений. См. документацию VK API.

- **Rate limiting**: Массовая загрузка файлов может вызвать срабатывание ограничений VK. Добавляйте задержки между загрузками при необходимости.
