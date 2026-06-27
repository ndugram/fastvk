from fastvk import FastVK
from fastvk.methods import GroupsGetMembers, MessagesGetHistory, WallGet
from fastvk.filters import Command
from fastvk.types import Message

bot = FastVK(token="vk1.a.YOUR_TOKEN")


@bot.message(Command("members"))
async def list_members(message: Message) -> None:
    members = await bot.collect(
        GroupsGetMembers,
        group_id=123,
        fields="photo_200",
        max_total=1000,
    )
    await message.answer(f"Участников (первые 1000): {len(members)}")


@bot.message(Command("posts"))
async def list_posts(message: Message) -> None:
    posts = await bot.collect(WallGet, owner_id=-123, count=50, max_total=200)
    await message.answer(f"Записей на стене: {len(posts)}")


@bot.message(Command("history"))
async def list_history(message: Message) -> None:
    history = await bot.collect(MessagesGetHistory, peer_id=2000000001, count=50)
    await message.answer(f"Сообщений в истории: {len(history)}")


if __name__ == "__main__":
    bot.run_polling()
