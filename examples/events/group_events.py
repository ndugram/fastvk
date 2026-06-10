"""
Обработка событий группы: join, leave, new wall post.
"""

from __future__ import annotations

import os

from fastvk import FastVK, Bot
from fastvk.types import Update, GroupJoinEvent, GroupLeaveEvent, WallPostEvent, User

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


@bot.group_join()
async def on_join(event: GroupJoinEvent, user: User, bot: Bot) -> None:
    await bot.messages.send(
        peer_id=event.user_id,
        message=f"Добро пожаловать, {user.first_name}! 🎉",
        random_id=0,
    )


@bot.group_leave()
async def on_leave(event: GroupLeaveEvent, user: User) -> None:
    action = "сам покинул" if event.is_self else "был исключён из"
    print(f"{user.full_name} (id={event.user_id}) {action} группы.")


@bot.wall_post_new()
async def on_post(event: WallPostEvent) -> None:
    print(f"Новый пост #{event.id}: {event.text[:80]!r}")


@bot.on("photo_new")
async def on_photo(update: Update) -> None:
    print(f"Новое фото: id={update.object.get('id')}")


if __name__ == "__main__":
    bot.run_polling()
