"""
SQLiteStorage — персистентный FSM без Redis.

Запуск:
    export VK_TOKEN=vk1.a.YOUR_TOKEN
    export VK_GROUP_ID=123456789
    python examples/advanced/sqlite_storage.py
"""

from __future__ import annotations

import os

from fastvk import FastVK
from fastvk.filters import Command, StateFilter
from fastvk.fsm import FSMContext, State, StatesGroup
from fastvk.fsm.sqlite import SQLiteStorage
from fastvk.types import Message

storage = SQLiteStorage("bot_fsm.db")
bot = FastVK(
    token=os.environ["VK_TOKEN"],
    group_id=int(os.environ["VK_GROUP_ID"]),
    storage=storage,
)


class Form(StatesGroup):
    waiting_name = State()
    waiting_age = State()


@bot.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.waiting_name)
    await message.answer("Как тебя зовут? (данные сохраняются в SQLite)")


@bot.message(StateFilter(Form.waiting_name))
async def got_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.waiting_age)
    await message.answer(f"Привет, {message.text}! Сколько тебе лет?")


@bot.message(StateFilter(Form.waiting_age))
async def got_age(message: Message, state: FSMContext) -> None:
    data = await state.update_data(age=message.text)
    await state.clear()
    await message.answer(
        f"Готово!\nИмя: {data['name']}\nВозраст: {data['age']}\n\n"
        "Данные сохранены в bot_fsm.db — перезапусти бота и проверь /status."
    )


@bot.message(Command("status"))
async def cmd_status(message: Message, state: FSMContext) -> None:
    s = await state.get_state()
    d = await state.get_data()
    if s is None and not d:
        await message.answer("Нет активного состояния.")
    else:
        await message.answer(f"Состояние: {s}\nДанные: {d}")


@bot.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменено.")


if __name__ == "__main__":
    bot.run_polling()
