# Message

The `Message` object is injected into every `message_new` handler. It exposes the full message data and convenient async methods.

## Sending a reply

```python
@bot.message()
async def echo(message: Message) -> None:
    await message.answer(message.text)          # sends to same peer
    await message.reply(message.text)           # quotes the original message
```

### answer() parameters

```python
await message.answer(
    "Hello!",
    keyboard=my_keyboard,           # Keyboard object or JSON string
    parse_mode=ParseMode.HTML,      # HTML or MARKDOWN formatting
    dont_parse_links=True,          # don't preview links
    disable_mentions=True,          # disable @mention notifications
)
```

## Sender info

`message.from_user` is always populated for `message_new` events:

```python
@bot.message()
async def greet(message: Message) -> None:
    user = message.from_user
    await message.answer(f"Hello, {user.first_name} {user.last_name}!")
    # or via DI:
    # async def greet(message: Message, user: User) -> None:
```

## Media shortcuts

```python
# photo
await message.answer_photo("photo-1_123456", caption="Look at this!")

# document
await message.answer_doc("doc-1_123456", caption="Here's the file")

# video
await message.answer_video("video-1_123456")

# sticker
await message.answer_sticker(9001)

# forward this message to another peer
await message.forward(peer_id=another_peer_id)
# or to same chat
await message.forward()
```

All media methods accept `keyboard=` and `dont_parse_links=` / `disable_mentions=`.

## Edit and delete

```python
# edit the message text
await message.edit("Updated text")
await message.edit("New text", keyboard=new_kb)

# delete
await message.delete()
await message.delete(delete_for_all=True)
```

!!! note
    `message.edit()` edits **this** received message, not a sent one. To edit a sent message, store the returned message ID and call `bot.messages.edit(...)` directly.

## Pin / unpin

```python
await message.pin()     # pin this message in the conversation
await message.unpin()   # unpin current pinned message
```

## Typing indicator

```python
from fastvk.enums import ChatAction

@bot.message(Command("slow"))
async def slow_reply(message: Message) -> None:
    await message.typing()                          # "typing..."
    await message.typing(ChatAction.AUDIO_MESSAGE)  # "recording audio..."
    await asyncio.sleep(2)
    await message.answer("Done!")
```

Available actions: `TYPING`, `AUDIO_MESSAGE`, `PHOTO`, `VIDEO`, `FILE`.

## Mark as read

```python
await message.mark_as_read()
```

## Search conversation

```python
@bot.message(Command("find"))
async def find_messages(message: Message) -> None:
    result = await message.search(q="hello", count=5)
    await message.answer(f"Found {result['count']} messages")
```

## Get history

```python
@bot.message(Command("recent"))
async def recent_messages(message: Message) -> None:
    history = await message.get_history(count=10)
    items = history.get("items", [])
    texts = [m.get("text", "")[:50] for m in items]
    await message.answer("\n".join(texts) if texts else "No messages")
```

## Invite link

```python
@bot.message(Command("invite"))
async def invite(message: Message) -> None:
    link = await message.get_invite_link()
    await message.answer(f"Invite link: {link}")
```

## Conversation members

```python
@bot.message(Command("members"))
async def members(message: Message) -> None:
    data = await message.get_conversation_members()
    count = data.get("count", 0)
    await message.answer(f"Members: {count}")
```

## Bookmark / restore

```python
await message.mark_as_important()          # bookmark this message
await message.restore()                     # restore if deleted
await message.get_by_conversation_message_id()  # get by local ID
```

## Message properties

```python
message.id          # int — message ID
message.date        # int — unix timestamp
message.peer_id     # int — conversation ID
message.from_id     # int — sender user ID
message.text        # str — message text
message.attachments # list[dict] — raw attachments
message.payload     # str | None — keyboard button payload
message.is_private  # bool — True if private message (peer_id < 2B)
message.is_chat     # bool — True if group chat
message.chat_id     # int | None — chat ID (peer_id - 2_000_000_000)
```
