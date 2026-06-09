"""
Webhook bot — принимает события от VK Callback API.

Требования:
  - Публичный HTTPS URL (ngrok, cloudflare tunnel и т.д.)
  - В настройках группы → API → Callback API: укажи URL и скопируй
    строку подтверждения в CONFIRMATION_TOKEN.

Запуск:
    export VK_TOKEN=vk1.a.YOUR_TOKEN
    export VK_GROUP_ID=123456789
    export VK_CONFIRMATION=YOUR_CONFIRMATION_CODE
    export VK_SECRET=your_optional_secret   # опционально
    python examples/advanced/webhook_bot.py
"""

from __future__ import annotations

import os

from fastvk import FastVK, Command
from fastvk.types import Message

bot = FastVK(
    token=os.environ["VK_TOKEN"],
    group_id=int(os.environ["VK_GROUP_ID"]),
)


@bot.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Привет! Я работаю через webhook.")


@bot.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("pong")


@bot.message()
async def echo(message: Message) -> None:
    if message.text:
        await message.answer(f"Ты написал: {message.text}")


if __name__ == "__main__":
    bot.run_webhook(
        confirmation_token=os.environ["VK_CONFIRMATION"],
        host="0.0.0.0",
        port=8080,
        path="/vk",
        secret=os.environ.get("VK_SECRET"),
    )
