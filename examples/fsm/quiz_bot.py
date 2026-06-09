"""
Викторина с тремя вопросами, счётом и итогом.
"""

from __future__ import annotations

import os

from fastvk import FastVK
from fastvk.filters import Command, StateFilter
from fastvk.fsm import FSMContext, State, StatesGroup
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))

QUESTIONS = [
    ("Столица Франции?", "париж"),
    ("Сколько будет 7 × 8?", "56"),
    ("Какой язык программирования самый лучший?", "python"),
]


class Quiz(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()


STATES = [Quiz.q1, Quiz.q2, Quiz.q3]


@bot.message(Command("quiz"))
async def cmd_quiz(message: Message, state: FSMContext) -> None:
    await state.set_state(Quiz.q1)
    await state.update_data(score=0)
    await message.answer(f"Вопрос 1/3: {QUESTIONS[0][0]}")


async def _check(message: Message, state: FSMContext, idx: int) -> None:
    question, answer = QUESTIONS[idx]
    data = await state.get_data()
    score = data.get("score", 0)
    correct = message.text.strip().lower() == answer

    if correct:
        score += 1
        await state.update_data(score=score)
        reply = "✅ Правильно!"
    else:
        reply = f"❌ Неверно. Правильный ответ: {answer.capitalize()}"

    if idx + 1 < len(QUESTIONS):
        await state.set_state(STATES[idx + 1])
        await message.answer(f"{reply}\n\nВопрос {idx + 2}/{len(QUESTIONS)}: {QUESTIONS[idx + 1][0]}")
    else:
        await state.clear()
        await message.answer(f"{reply}\n\nВикторина окончена! Результат: {score}/{len(QUESTIONS)}")


@bot.message(StateFilter(Quiz.q1))
async def answer_q1(message: Message, state: FSMContext) -> None:
    await _check(message, state, 0)


@bot.message(StateFilter(Quiz.q2))
async def answer_q2(message: Message, state: FSMContext) -> None:
    await _check(message, state, 1)


@bot.message(StateFilter(Quiz.q3))
async def answer_q3(message: Message, state: FSMContext) -> None:
    await _check(message, state, 2)


if __name__ == "__main__":
    bot.run_polling()
