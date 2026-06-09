"""
Инъекция User — фреймворк подтягивает профиль через users.get автоматически.
"""

from __future__ import annotations

import os

from fastvk import FastVK, Bot
from fastvk.filters import Command
from fastvk.types import Message, User

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


@bot.message(Command("me"))
async def cmd_me(message: Message, user: User) -> None:
    await message.answer(f"Ты: {user.full_name} (id{user.id})")


@bot.message(Command("friends"))
async def cmd_friends(message: Message, bot: Bot) -> None:
    data = await bot.friends.get(user_id=message.from_id, count=5)
    ids = data.get("items", [])
    await message.answer(f"Первые друзья: {ids}")


if __name__ == "__main__":
    bot.run_polling()
