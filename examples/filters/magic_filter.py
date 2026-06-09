"""
F magic filter — все варианты использования.
"""

from __future__ import annotations

import os

from fastvk import F, FastVK, Button, CallbackQuery, Keyboard
from fastvk.filters import Command, StateFilter
from fastvk.fsm import FSMContext, State, StatesGroup
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


# =============================================================================
# Точное совпадение текста
# =============================================================================

@bot.message(F.text == "привет")
async def on_hi(message: Message) -> None:
    await message.answer("Привет!")


@bot.message(F.text == "пока")
async def on_bye(message: Message) -> None:
    await message.answer("Пока!")


# =============================================================================
# Строковые операции
# =============================================================================

@bot.message(F.text.startswith("/"))
async def on_any_cmd(message: Message) -> None:
    await message.answer(f"Неизвестная команда: {message.text}")


@bot.message(F.text.endswith("?"))
async def on_question(message: Message) -> None:
    await message.answer("Хороший вопрос! Пока не знаю ответа 🤷")


@bot.message(F.text.contains("скидка") | F.text.contains("акция"))
async def on_promo(message: Message) -> None:
    await message.answer("Напиши /promo чтобы узнать про акции!")


# =============================================================================
# in_ / not_in_
# =============================================================================

@bot.message(F.text.in_("стоп", "отмена", "cancel", "отменить"))
async def on_stop(message: Message) -> None:
    await message.answer("Понял, останавливаю.")


@bot.message(F.from_id.in_(111111111, 222222222))
async def on_vip(message: Message) -> None:
    await message.answer("Привет, VIP!")


# =============================================================================
# Инверсия ~
# =============================================================================

@bot.message(~F.text.startswith("/") & ~F.text.startswith("http"))
async def on_plain_text(message: Message) -> None:
    await message.answer(f"Ты написал: {message.text}")


# =============================================================================
# Комбинации & и |
# =============================================================================

@bot.message(F.text.contains("купить") | F.text.contains("купи"))
async def on_buy_intent(message: Message) -> None:
    await message.answer("Хочешь что-то купить? Напиши /catalog")


@bot.message(F.from_id == 123456789, F.text.startswith("/admin"))
async def on_admin_cmd(message: Message) -> None:
    await message.answer("Админ-команда выполнена.")


# =============================================================================
# Проверка поля (truthy check)
# =============================================================================

# F.text — True если текст непустой
@bot.message(F.text)
async def on_has_text(message: Message) -> None:
    await message.answer(f"Длина сообщения: {len(message.text)} символов")


# =============================================================================
# Callback + F.payload
# =============================================================================

@bot.message(Command("vote"))
async def cmd_vote(message: Message) -> None:
    kb = (
        Keyboard(inline=True)
        .row(
            Button.callback("👍 Да",  payload={"action": "yes", "v": 1}),
            Button.callback("👎 Нет", payload={"action": "no",  "v": 0}),
        )
    )
    await message.answer("Голосуй:", keyboard=kb)


@bot.callback(F.payload == {"action": "yes", "v": 1})
async def on_yes(callback: CallbackQuery) -> None:
    await callback.answer("Ты выбрал Да! ✅")


@bot.callback(F.payload == {"action": "no", "v": 0})
async def on_no(callback: CallbackQuery) -> None:
    await callback.answer("Ты выбрал Нет! ❌")


# =============================================================================
# Вложенный путь по payload dict — F.payload.action
# =============================================================================

@bot.message(Command("shop"))
async def cmd_shop(message: Message) -> None:
    kb = (
        Keyboard(inline=True)
        .row(
            Button.callback("🛒 Купить",  payload={"action": "buy"}),
            Button.callback("↩️ Вернуть", payload={"action": "refund"}),
        )
    )
    await message.answer("Выбери действие:", keyboard=kb)


@bot.callback(F.payload.action == "buy")
async def on_buy(callback: CallbackQuery) -> None:
    await callback.answer("Оформляю заказ!")


@bot.callback(F.payload.action == "refund")
async def on_refund(callback: CallbackQuery) -> None:
    await callback.answer("Оформляю возврат...")


# =============================================================================
# FSM + F
# =============================================================================

class Form(StatesGroup):
    waiting = State()


@bot.message(Command("form"))
async def cmd_form(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.waiting)
    await message.answer("Напиши своё имя:")


@bot.message(StateFilter(Form.waiting), F.text)
async def got_name(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(f"Привет, {message.text}!")


@bot.message(StateFilter(Form.waiting), ~F.text)
async def got_no_text(message: Message) -> None:
    await message.answer("Нужно именно текст, без стикеров и файлов!")


if __name__ == "__main__":
    bot.run_polling()
