"""
Прямые вызовы VK API через инжектированный Bot.
"""

from __future__ import annotations

import os

from fastvk import FastVK, Bot
from fastvk.filters import Command
from fastvk.types import Message, User

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


@bot.message(Command("members"))
async def cmd_members(message: Message, bot: Bot) -> None:
    data = await bot.groups.getMembers(
        group_id=int(os.environ["VK_GROUP_ID"]),
        count=1,
    )
    await message.answer(f"Участников в группе: {data['count']}")


@bot.message(Command("me"))
async def cmd_me(message: Message, user: User) -> None:
    await message.answer(f"Ты: {user.full_name} (id{user.id})")


@bot.message(Command("wall"))
async def cmd_wall(message: Message, bot: Bot) -> None:
    data = await bot.wall.get(
        owner_id=-int(os.environ["VK_GROUP_ID"]),
        count=3,
    )
    posts = data.get("items", [])
    if not posts:
        await message.answer("Постов нет.")
        return
    lines = [f"#{p['id']}: {(p.get('text') or '—')[:60]}" for p in posts]
    await message.answer("Последние посты:\n" + "\n".join(lines))


@bot.message(Command("online"))
async def cmd_online(message: Message, bot: Bot) -> None:
    data = await bot.groups.getOnlineStatus(group_id=int(os.environ["VK_GROUP_ID"]))
    status = data.get("status", "unknown")
    await message.answer(f"Онлайн-статус группы: {status}")


if __name__ == "__main__":
    bot.run_polling()
