"""
Демонстрация встроенных фильтров: Command, Text, FromUser, IsChat.
"""

from __future__ import annotations

import os

from fastvk import FastVK
from fastvk.filters import Command, FromUser, IsChat, Text
from fastvk.types import Message

ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


@bot.message(Command("start", "hello"))
async def cmd_start(message: Message) -> None:
    await message.answer("Команда /start или /hello")


@bot.message(Text("привет", ignore_case=True))
async def on_hi(message: Message) -> None:
    await message.answer("Привет!")


@bot.message(Text("купить", contains=True, ignore_case=True))
async def on_buy_mention(message: Message) -> None:
    await message.answer("Хочешь что-то купить? Напиши /shop")


@bot.message(IsChat("private"))
async def private_only(message: Message) -> None:
    await message.answer("Это личка, привет!")


@bot.message(IsChat("chat"))
async def chat_only(message: Message) -> None:
    await message.answer("Это чат, привет всем!")


@bot.message(FromUser(ADMIN_ID), Command("secret"))
async def admin_secret(message: Message) -> None:
    await message.answer("Секретная команда только для админа!")


if __name__ == "__main__":
    bot.run_polling()
