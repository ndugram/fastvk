"""
Кастомные фильтры — любой callable(event, context) -> bool.
"""

from __future__ import annotations

import os
from typing import Any

from fastvk import FastVK
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


def is_long(message: Message, data: dict[str, Any]) -> bool:
    """Сообщение длиннее 100 символов."""
    return len(message.text or "") > 100


def is_question(message: Message, data: dict[str, Any]) -> bool:
    """Сообщение оканчивается на '?'."""
    return (message.text or "").strip().endswith("?")


class HasKeyword:
    """Фильтр-класс: сообщение содержит одно из ключевых слов."""

    def __init__(self, *keywords: str) -> None:
        self.keywords = {kw.lower() for kw in keywords}

    def __call__(self, message: Message, data: dict[str, Any]) -> bool:
        text = (message.text or "").lower()
        return any(kw in text for kw in self.keywords)


@bot.message(is_long)
async def on_long(message: Message) -> None:
    await message.answer(f"Длинное сообщение ({len(message.text or '')} символов)!")


@bot.message(is_question)
async def on_question(message: Message) -> None:
    await message.answer("Ты задал вопрос! Я пока не знаю ответа 🤷")


@bot.message(HasKeyword("скидка", "акция", "промокод"))
async def on_promo(message: Message) -> None:
    await message.answer("Напиши /promo чтобы узнать про акции!")


@bot.message()
async def fallback(message: Message) -> None:
    await message.answer("Обычное сообщение.")


if __name__ == "__main__":
    bot.run_polling()
