"""
Обработка событий группы: join, leave, new wall post.
"""

from __future__ import annotations

import os

from fastvk import FastVK, Bot
from fastvk.types import Update

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


@bot.group_join()
async def on_join(event: dict, bot: Bot) -> None:
    user_id = event.get("user_id")
    if user_id:
        await bot.messages.send(
            peer_id=user_id,
            message="Добро пожаловать в группу! 🎉",
            random_id=0,
        )


@bot.group_leave()
async def on_leave(event: dict) -> None:
    user_id = event.get("user_id")
    print(f"Пользователь {user_id} покинул группу.")


@bot.wall_post_new()
async def on_post(event: dict) -> None:
    post_id = event.get("id")
    text    = event.get("text", "")[:80]
    print(f"Новый пост #{post_id}: {text!r}")


@bot.on("photo_new")
async def on_photo(update: Update) -> None:
    print(f"Новое фото: id={update.object.get('id')}")


if __name__ == "__main__":
    bot.run_polling()
