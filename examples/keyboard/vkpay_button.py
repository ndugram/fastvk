"""
VK Pay кнопки: оплата и переводы.

Запуск:
    export VK_TOKEN=vk1.a.YOUR_TOKEN
    export VK_GROUP_ID=123456789
    python examples/keyboard/vkpay_button.py
"""

from __future__ import annotations

import os

from fastvk import FastVK, Button, Keyboard
from fastvk.filters import Command
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))

GROUP_ID = int(os.environ["VK_GROUP_ID"])


@bot.message(Command("pay"))
async def cmd_pay(message: Message) -> None:
    kb = (
        Keyboard(inline=True)
        .row(
            Button.vkpay(
                action="pay-to-group",
                group_id=GROUP_ID,
                amount=100,
                description="Донат боту",
            )
        )
    )
    await message.answer("Поддержи бота:", keyboard=kb)


@bot.message(Command("transfer"))
async def cmd_transfer(message: Message) -> None:
    kb = (
        Keyboard(inline=True)
        .row(
            Button.vkpay(action="transfer-to-group", group_id=GROUP_ID, aid=1)
        )
    )
    await message.answer("Перевод в группу:", keyboard=kb)


@bot.message(Command("donate"))
async def cmd_donate(message: Message) -> None:
    kb = (
        Keyboard(inline=True)
        .row(Button.vkpay(action="pay-to-group", group_id=GROUP_ID, amount=50, description="50 руб"))
        .row(Button.vkpay(action="pay-to-group", group_id=GROUP_ID, amount=100, description="100 руб"))
        .row(Button.vkpay(action="pay-to-group", group_id=GROUP_ID, amount=500, description="500 руб"))
    )
    await message.answer("Выбери сумму доната:", keyboard=kb)


if __name__ == "__main__":
    bot.run_polling()
