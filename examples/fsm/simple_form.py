"""
Простая форма из двух шагов: имя → возраст.
"""

from __future__ import annotations

import os

from fastvk import FastVK
from fastvk.filters import Command, StateFilter
from fastvk.fsm import FSMContext, State, StatesGroup
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


class Form(StatesGroup):
    waiting_name = State()
    waiting_age  = State()


@bot.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.waiting_name)
    await message.answer("Как тебя зовут?")


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
        f"Записал!\n"
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}"
    )


@bot.message(Command("cancel"), StateFilter(Form.waiting_name, Form.waiting_age))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменено.")


if __name__ == "__main__":
    bot.run_polling()
