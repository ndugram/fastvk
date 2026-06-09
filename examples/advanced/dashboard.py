"""
Dashboard example — bot info + live stats at http://localhost:8080
"""
from fastvk import FastVK, Router
from fastvk.types import Message

BOT_TOKEN=""
GROUP_ID = 1234567

bot = FastVK(
    token=BOT_TOKEN,
    group_id=GROUP_ID,
    dashboard=True,
)

router = Router()
bot.include_router(router)


@router.message()
async def echo(message: Message) -> None:
    await message.answer(message.text or "нет текста")
    await message.answer(message.from_user.full_name)


@router.exception_handler()
async def error(message: Message) -> None:
    await message.answer("Возникла ошибка")


if __name__ == "__main__":
    bot.run_polling()
    # open http://localhost:8080
