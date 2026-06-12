"""
Example: Upload media files (photos, documents, audio messages)

This example demonstrates how to use the Uploader class to upload
various types of media files to VK messages.
"""

from fastvk import FastVK, Uploader
from fastvk.filters import Command
from fastvk.types import Message


bot = FastVK(token="vk1.a.YOUR_TOKEN")
uploader = Uploader(bot.bot)


@bot.message(Command("photo"))
async def send_photo(message: Message) -> None:
    """Upload and send a photo."""
    try:
        # Upload photo from file path
        attachment = await uploader.photo(
            peer_id=message.peer_id,
            file="path/to/photo.jpg"
        )
        await message.answer_photo(attachment, caption="Вот фото!")
    except FileNotFoundError:
        await message.answer("Файл не найден. Убедитесь, что путь правильный.")
    except Exception as e:
        await message.answer(f"Ошибка загрузки: {e}")


@bot.message(Command("document"))
async def send_document(message: Message) -> None:
    """Upload and send a document."""
    try:
        attachment = await uploader.document(
            peer_id=message.peer_id,
            file="path/to/document.pdf",
            title="Важный документ"
        )
        await message.answer_doc(attachment, caption="Документ загружен!")
    except FileNotFoundError:
        await message.answer("Файл не найден.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@bot.message(Command("voice"))
async def send_voice(message: Message) -> None:
    """Upload and send an audio message (voice)."""
    try:
        # Upload audio message (should be OGG/Opus format)
        attachment = await uploader.audio_message(
            peer_id=message.peer_id,
            file="path/to/voice.ogg"
        )
        # Audio messages are sent without caption text
        await message.answer_doc(attachment)
    except FileNotFoundError:
        await message.answer("Аудиофайл не найден.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@bot.message(Command("graffiti"))
async def send_graffiti(message: Message) -> None:
    """Upload and send a graffiti (drawing)."""
    try:
        attachment = await uploader.graffiti(
            peer_id=message.peer_id,
            file="path/to/drawing.png"
        )
        await message.answer_doc(attachment, caption="Граффити!")
    except FileNotFoundError:
        await message.answer("Файл не найден.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@bot.message(Command("multi"))
async def send_multiple(message: Message) -> None:
    """Upload and send multiple attachments."""
    try:
        # Upload multiple files
        photo1 = await uploader.photo(message.peer_id, "photo1.jpg")
        photo2 = await uploader.photo(message.peer_id, "photo2.jpg")
        doc = await uploader.document(message.peer_id, "file.pdf", title="PDF файл")

        # Combine attachments (comma-separated)
        attachments = f"{photo1},{photo2},{doc}"

        # Use bot.messages.send directly for multiple attachments
        await message._bot.messages.send(
            peer_id=message.peer_id,
            message="Несколько файлов:",
            attachment=attachments,
            random_id=0
        )
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@bot.message(Command("from_bytes"))
async def send_from_bytes(message: Message) -> None:
    """Upload from bytes (file-like object)."""
    import io

    try:
        # Create a simple text file in memory
        file_content = b"Hello from FastVK uploader!"
        file_obj = io.BytesIO(file_content)

        attachment = await uploader.document(
            peer_id=message.peer_id,
            file=file_obj,
            filename="test.txt",
            title="Текстовый файл"
        )
        await message.answer_doc(attachment, caption="Файл из памяти!")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


if __name__ == "__main__":
    print("Bot started. Available commands:")
    print("  /photo     - Upload and send a photo")
    print("  /document  - Upload and send a document")
    print("  /voice     - Upload and send an audio message")
    print("  /graffiti  - Upload and send a graffiti")
    print("  /multi     - Upload multiple files at once")
    print("  /from_bytes - Upload file from memory")
    bot.run_polling()
