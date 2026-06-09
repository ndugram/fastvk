"""
Обработка команд /start, /help, /ping.
"""

from __future__ import annotations

import os

from fastvk import FastVK
from fastvk.filters import Command
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


@bot.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я FastVK бот.\n"
        "Команды:\n"
        "/start — это сообщение\n"
        "/help  — помощь\n"
        "/ping  — проверка связи"
    )


@bot.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer("Напиши что-нибудь — я отвечу!")


@bot.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("pong 🏓")


@bot.message()
async def fallback(message: Message) -> None:
    await message.answer(f"Ты написал: {message.text!r}")


if __name__ == "__main__":
    bot.run_polling()
