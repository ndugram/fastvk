"""
Inline-клавиатура с callback-кнопками и обработчиком нажатий.
"""

from __future__ import annotations

import os

from fastvk import FastVK, Button, CallbackQuery, Keyboard
from fastvk.filters import Command
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


@bot.message(Command("vote"))
async def cmd_vote(message: Message) -> None:
    kb = (
        Keyboard(inline=True)
        .row(
            Button.callback("👍 Нравится", payload={"action": "like"}),
            Button.callback("👎 Не нравится", payload={"action": "dislike"}),
        )
        .row(Button.link("Документация", url="https://github.com"))
    )
    await message.answer("Как тебе FastVK?", keyboard=kb)


@bot.message(Command("confirm"))
async def cmd_confirm(message: Message) -> None:
    kb = (
        Keyboard(inline=True)
        .row(
            Button.callback("✅ Да",    payload={"ans": True}),
            Button.callback("❌ Нет",   payload={"ans": False}),
        )
    )
    await message.answer("Подтверди действие:", keyboard=kb)


@bot.callback()
async def on_callback(callback: CallbackQuery) -> None:
    action = callback.payload.get("action")
    ans    = callback.payload.get("ans")

    if action == "like":
        await callback.answer("Спасибо! ❤️")
    elif action == "dislike":
        await callback.answer("Понял, буду лучше!")
    elif ans is True:
        await callback.answer("Подтверждено ✅")
    elif ans is False:
        await callback.answer("Отменено ❌")
    else:
        await callback.answer(f"payload: {callback.payload}")


if __name__ == "__main__":
    bot.run_polling()
