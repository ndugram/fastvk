"""
FSM + клавиатура: выбор варианта кнопками вместо ввода текста.
"""

from __future__ import annotations

import os

from fastvk import FastVK, Button, Keyboard
from fastvk.filters import Command, StateFilter, Text
from fastvk.fsm import FSMContext, State, StatesGroup
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))

YES_NO_KB = (
    Keyboard(one_time=True)
    .row(Button.text("✅ Да", color="positive"), Button.text("❌ Нет", color="negative"))
)


class Order(StatesGroup):
    confirm = State()
    size    = State()


@bot.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext) -> None:
    await state.set_state(Order.confirm)
    await message.answer("Хочешь сделать заказ?", keyboard=YES_NO_KB)


@bot.message(StateFilter(Order.confirm), Text("✅ Да"))
async def order_yes(message: Message, state: FSMContext) -> None:
    await state.set_state(Order.size)
    kb = (
        Keyboard(one_time=True)
        .row(
            Button.text("S", color="secondary"),
            Button.text("M", color="primary"),
            Button.text("L", color="secondary"),
        )
    )
    await message.answer("Выбери размер:", keyboard=kb)


@bot.message(StateFilter(Order.confirm), Text("❌ Нет"))
async def order_no(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Заказ отменён.", keyboard=Keyboard.remove())


@bot.message(StateFilter(Order.size), Text("S", "M", "L"))
async def order_size(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(f"Заказ оформлен! Размер: {message.text}", keyboard=Keyboard.remove())


if __name__ == "__main__":
    bot.run_polling()
