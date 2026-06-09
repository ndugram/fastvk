"""
Простейший эхо-бот — повторяет любое входящее сообщение.
"""

from __future__ import annotations

import os

from fastvk import FastVK
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


@bot.message()
async def echo(message: Message) -> None:
    await message.answer(message.text)


if __name__ == "__main__":
    bot.run_polling()
