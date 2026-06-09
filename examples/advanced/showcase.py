"""
Полный справочник возможностей FastVK.

Запуск:
    VK_TOKEN=vk1.a.YOUR_TOKEN VK_GROUP_ID=123456789 python examples/advanced/showcase.py
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Awaitable, Callable
from typing import Any

from fastvk import FastVK, Bot, Button, CallbackQuery, Keyboard, Router
from fastvk.filters import Command, FromUser, IsChat, StateFilter, Text
from fastvk.fsm import FSMContext, State, StatesGroup
from fastvk.middleware import BaseMiddleware
from fastvk.types import Message, User

logging.basicConfig(level=logging.INFO)

ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# =============================================================================
# MIDDLEWARE
# =============================================================================

class TimingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        t = time.monotonic()
        result = await handler(event, data)
        logging.getLogger("fastvk").info("%.3f сек", time.monotonic() - t)
        return result


# =============================================================================
# РОУТЕРЫ
# =============================================================================

admin_router = Router()
user_router  = Router()

# =============================================================================
# ПРИЛОЖЕНИЕ
# =============================================================================

bot = FastVK(
    token=os.environ["VK_TOKEN"],
    group_id=int(os.environ["VK_GROUP_ID"]),
    middleware=[TimingMiddleware()],
)
bot.include_router(admin_router)
bot.include_router(user_router)

# =============================================================================
# ОСНОВНЫЕ КОМАНДЫ
# =============================================================================

@bot.message(Command("start"))
async def cmd_start(message: Message) -> None:
    kb = (
        Keyboard(one_time=True)
        .row(Button.text("📋 Меню", color="primary"), Button.text("ℹ️ О боте"))
        .row(Button.text("🎯 Викторина", color="secondary"))
    )
    await message.answer("Привет! Я FastVK бот 🤖\nВыбери действие:", keyboard=kb)


@bot.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Команды:\n"
        "/start    — главное меню\n"
        "/me       — профиль\n"
        "/vote     — голосование\n"
        "/register — анкета\n"
        "/quiz     — викторина\n"
        "/cancel   — отмена"
    )


@bot.message(Command("me"))
async def cmd_me(message: Message, user: User) -> None:
    await message.answer(f"Ты: {user.full_name} (id{user.id})")


# =============================================================================
# INLINE КЛАВИАТУРА И CALLBACKS
# =============================================================================

@bot.message(Command("vote"))
async def cmd_vote(message: Message) -> None:
    kb = (
        Keyboard(inline=True)
        .row(
            Button.callback("👍 Нравится",     payload={"v": "like"}),
            Button.callback("👎 Не нравится",  payload={"v": "dislike"}),
        )
        .row(Button.link("GitHub", url="https://github.com"))
    )
    await message.answer("Как тебе FastVK?", keyboard=kb)


@bot.callback()
async def on_vote(callback: CallbackQuery) -> None:
    v = callback.payload.get("v")
    if v == "like":
        await callback.answer("Спасибо! ❤️")
    elif v == "dislike":
        await callback.answer("Понял, буду лучше!")
    else:
        await callback.answer(f"payload={callback.payload}")

# =============================================================================
# FSM
# =============================================================================

class RegistrationForm(StatesGroup):
    waiting_name = State()
    waiting_age  = State()


class QuizGame(StatesGroup):
    q1 = State()
    q2 = State()


@bot.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationForm.waiting_name)
    await message.answer("Как тебя зовут?")


@bot.message(StateFilter(RegistrationForm.waiting_name))
async def fsm_got_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(RegistrationForm.waiting_age)
    await message.answer(f"Отлично, {message.text}! Сколько тебе лет?")


@bot.message(StateFilter(RegistrationForm.waiting_age))
async def fsm_got_age(message: Message, state: FSMContext) -> None:
    data = await state.update_data(age=message.text)
    await state.clear()
    await message.answer(f"Готово!\nИмя: {data['name']}\nВозраст: {data['age']}")


@bot.message(Command("quiz"))
async def cmd_quiz(message: Message, state: FSMContext) -> None:
    await state.set_state(QuizGame.q1)
    await message.answer("Вопрос 1: Столица Франции?")


@bot.message(StateFilter(QuizGame.q1))
async def quiz_q1(message: Message, state: FSMContext) -> None:
    correct = message.text.strip().lower() == "париж"
    await state.update_data(score=1 if correct else 0)
    await state.set_state(QuizGame.q2)
    result = "✅" if correct else "❌ Правильно: Париж"
    await message.answer(f"{result}\nВопрос 2: 7 × 8 = ?")


@bot.message(StateFilter(QuizGame.q2))
async def quiz_q2(message: Message, state: FSMContext) -> None:
    correct = message.text.strip() == "56"
    data = await state.get_data()
    score = data.get("score", 0) + (1 if correct else 0)
    await state.clear()
    result = "✅" if correct else "❌ Правильно: 56"
    await message.answer(f"{result}\nРезультат: {score}/2")


@bot.message(Command("cancel"), StateFilter(
    RegistrationForm.waiting_name,
    RegistrationForm.waiting_age,
    QuizGame.q1,
    QuizGame.q2,
))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменено.")

# =============================================================================
# ФИЛЬТРЫ
# =============================================================================

@bot.message(Text("📋 Меню"))
async def on_menu(message: Message) -> None:
    await message.answer("Меню: /help")


@bot.message(Text("ℹ️ О боте"))
async def on_about(message: Message, bot: Bot) -> None:
    await message.answer("Бот на FastVK. github.com/ndugram/fastvk")


@bot.message(Text("🎯 Викторина"))
async def on_quiz_btn(message: Message, state: FSMContext) -> None:
    await cmd_quiz(message, state)


@bot.message(IsChat("private"), Text("помощь", contains=True, ignore_case=True))
async def on_help_mention(message: Message) -> None:
    await message.answer("Напиши /help")

# =============================================================================
# АДМИН
# =============================================================================

@admin_router.message(FromUser(ADMIN_ID), Command("stats"))
async def admin_stats(message: Message, bot: Bot) -> None:
    data = await bot.groups.getMembers(group_id=int(os.environ["VK_GROUP_ID"]), count=1)
    await message.answer(f"Участников: {data['count']}")

# =============================================================================
# СОБЫТИЯ ГРУППЫ
# =============================================================================

@bot.group_join()
async def on_join(event: dict, bot: Bot) -> None:
    user_id = event.get("user_id")
    if user_id:
        await bot.messages.send(peer_id=user_id, message="Добро пожаловать! 🎉", random_id=0)


@bot.group_leave()
async def on_leave(event: dict) -> None:
    print(f"Покинул группу: {event.get('user_id')}")

# =============================================================================
# FALLBACK
# =============================================================================

@bot.message()
async def fallback(message: Message) -> None:
    await message.answer("Не понял. Напиши /help")

# =============================================================================
# ЗАПУСК
# =============================================================================

if __name__ == "__main__":
    bot.run_polling()
