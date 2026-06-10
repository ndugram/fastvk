"""
Dashboard bot example.

Settings are defined in settings.py as a BaseDashboard subclass.
Pass the instance to FastVK as `dashboard=`.

Dashboard available at http://127.0.0.1:8000 when running.
"""
from fastvk import FastVK, Router
from fastvk.types import Message

from examples.dashboard.settings import dashboard

BOT_TOKEN = ""
GROUP_ID = 1234567

bot = FastVK(
    token=BOT_TOKEN,
    group_id=GROUP_ID,
    dashboard=dashboard,
)

router = Router()
bot.include_router(router)


@router.message()
async def echo(message: Message) -> None:
    await message.answer(message.text or "нет текста")


@router.exception_handler()
async def on_error(message: Message) -> None:
    await message.answer("Возникла ошибка")


if __name__ == "__main__":
    bot.run_polling()
