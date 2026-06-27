from fastvk import FastVK
from fastvk.filters import Command
from fastvk.types import Message

bot = FastVK(token="vk1.a.YOUR_TOKEN")


@bot.message(Command("chat"))
async def create_and_invite(message: Message) -> None:
    chat_id = await bot.messages.createChat(
        title="My Chat",
        peer_ids=[message.from_id],
    )
    await message.answer(f"Chat created: {chat_id}")


@bot.message(Command("search"))
async def search_messages(message: Message) -> None:
    result = await message.search(q="hello", count=5)
    count = result.get("count", 0)
    items = result.get("items", [])
    await message.answer(f"Found {count} messages, showing {len(items)}")


@bot.message(Command("link"))
async def invite_link(message: Message) -> None:
    link = await message.get_invite_link()
    await message.answer(f"Invite link: {link}")


@bot.message(Command("pin"))
async def pin_this(message: Message) -> None:
    await message.pin()
    await message.answer("Pinned!")


@bot.message(Command("history"))
async def show_history(message: Message) -> None:
    history = await message.get_history(count=5)
    items = history.get("items", [])
    lines = [f"[{m['date']}] {m.get('text', '')[:50]}" for m in items]
    await message.answer("Last messages:\n" + "\n".join(lines) if lines else "No messages")


if __name__ == "__main__":
    bot.run_polling()
