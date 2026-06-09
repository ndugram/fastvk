"""
Обычная клавиатура (появляется под полем ввода).
"""

from __future__ import annotations

import os

from fastvk import FastVK, Button, Keyboard
from fastvk.filters import Command, Text
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))

MAIN_KB = (
    Keyboard(one_time=False)
    .row(Button.text("📋 Меню",    color="primary"))
    .row(Button.text("ℹ️ О боте",  color="secondary"), Button.text("❌ Закрыть", color="negative"))
)


@bot.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Выбери действие:", keyboard=MAIN_KB)


@bot.message(Text("📋 Меню"))
async def on_menu(message: Message) -> None:
    await message.answer("Это главное меню!")


@bot.message(Text("ℹ️ О боте"))
async def on_about(message: Message) -> None:
    await message.answer("Бот на FastVK 🤖")


@bot.message(Text("❌ Закрыть"))
async def on_close(message: Message) -> None:
    await message.answer("Клавиатура убрана.", keyboard=Keyboard.remove())


if __name__ == "__main__":
    bot.run_polling()
