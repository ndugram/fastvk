# Сообщение

Объект `Message` передаётся в каждый хэндлер события `message_new`. Он содержит данные сообщения и удобные async методы.

## Отправка ответа

```python
@bot.message()
async def echo(message: Message) -> None:
    await message.answer(message.text)        # отправляет в тот же чат
    await message.reply(message.text)         # цитирует исходное сообщение
```

### Параметры answer()

```python
await message.answer(
    "Привет!",
    keyboard=my_keyboard,           # объект Keyboard или JSON строка
    parse_mode=ParseMode.HTML,      # форматирование HTML или MARKDOWN
    dont_parse_links=True,          # не превью ссылок
    disable_mentions=True,          # отключить уведомления @mention
)
```

## Информация об отправителе

`message.from_user` всегда заполнен для событий `message_new`:

```python
@bot.message()
async def greet(message: Message) -> None:
    user = message.from_user
    await message.answer(f"Привет, {user.first_name} {user.last_name}!")
    # или через DI:
    # async def greet(message: Message, user: User) -> None:
```

## Медиа шорткаты

```python
# фото
await message.answer_photo("photo-1_123456", caption="Смотри!")

# документ
await message.answer_doc("doc-1_123456", caption="Вот файл")

# видео
await message.answer_video("video-1_123456")

# стикер
await message.answer_sticker(9001)

# переслать это сообщение в другой чат
await message.forward(peer_id=another_peer_id)
# или в тот же чат
await message.forward()
```

Все медиа методы принимают `keyboard=`, `dont_parse_links=` и `disable_mentions=`.

## Редактирование и удаление

```python
# изменить текст сообщения
await message.edit("Обновлённый текст")
await message.edit("Новый текст", keyboard=new_kb)

# удалить
await message.delete()
await message.delete(delete_for_all=True)
```

!!! note
    `message.edit()` редактирует **принятое** сообщение, а не отправленное. Чтобы редактировать отправленное, сохрани его ID и вызови `bot.messages.edit(...)` напрямую.

## Закрепление

```python
await message.pin()     # закрепить сообщение в беседе
await message.unpin()   # открепить текущее закреплённое
```

## Индикатор набора текста

```python
from fastvk.enums import ChatAction

@bot.message(Command("slow"))
async def slow_reply(message: Message) -> None:
    await message.typing()                          # "печатает..."
    await message.typing(ChatAction.AUDIO_MESSAGE)  # "записывает аудио..."
    await asyncio.sleep(2)
    await message.answer("Готово!")
```

Доступные действия: `TYPING`, `AUDIO_MESSAGE`, `PHOTO`, `VIDEO`, `FILE`.

## Прочитать сообщение

```python
await message.mark_as_read()
```

## Свойства сообщения

```python
message.id          # int — ID сообщения
message.date        # int — unix timestamp
message.peer_id     # int — ID беседы
message.from_id     # int — ID отправителя
message.text        # str — текст сообщения
message.attachments # list[dict] — вложения (raw)
message.payload     # str | None — payload кнопки клавиатуры
message.is_private  # bool — True если личное сообщение
message.is_chat     # bool — True если групповой чат
message.chat_id     # int | None — ID чата (peer_id - 2_000_000_000)
```
