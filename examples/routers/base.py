"""
Разбивка хэндлеров по роутерам — shop, support, fallback.
"""

from __future__ import annotations

import os

from fastvk import FastVK, Router
from fastvk.filters import Command, Text
from fastvk.types import Message

# ── роутеры ──────────────────────────────────────────────────────────────────

shop_router    = Router()
support_router = Router()

# ── shop ─────────────────────────────────────────────────────────────────────

@shop_router.message(Command("catalog"))
async def catalog(message: Message) -> None:
    await message.answer("📦 Наш каталог: ...")


@shop_router.message(Command("cart"))
async def cart(message: Message) -> None:
    await message.answer("🛒 Твоя корзина пуста.")


@shop_router.message(Text("цена", contains=True, ignore_case=True))
async def price_mention(message: Message) -> None:
    await message.answer("Цены начинаются от 99₽. Напиши /catalog")

# ── support ──────────────────────────────────────────────────────────────────

@support_router.message(Command("support"))
async def support(message: Message) -> None:
    await message.answer("Служба поддержки: @support")


@support_router.message(Text("помогите", "помощь", contains=True, ignore_case=True))
async def help_request(message: Message) -> None:
    await message.answer("Чем могу помочь? Напиши /support")

# ── приложение ────────────────────────────────────────────────────────────────

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))
bot.include_router(shop_router)
bot.include_router(support_router)


@bot.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Команды:\n/catalog — каталог\n/cart — корзина\n/support — поддержка")


@bot.message()
async def fallback(message: Message) -> None:
    await message.answer("Не понял. Напиши /start")


if __name__ == "__main__":
    bot.run_polling()
