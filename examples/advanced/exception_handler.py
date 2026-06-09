"""
Exception handler example — @bot.exception_handler() (FastAPI-style).

Handlers receive the exception and any DI-injected types (Message, Bot, etc.)
"""
from fastvk import FastVK, Router
from fastvk.exceptions import VKAPIError
from fastvk.types import Message

TOKEN = "vk1.a.YOUR_TOKEN"
GROUP_ID = 123456789

bot = FastVK(token=TOKEN, group_id=GROUP_ID)
router = Router()
bot.include_router(router)


# --- handlers ---

@router.message()
async def echo(message: Message) -> None:
    if message.text == "crash":
        raise RuntimeError("намеренный краш")
    if message.text == "vk":
        raise VKAPIError({"error_code": 999, "error_msg": "fake VK error"})
    await message.answer(message.text or "нет текста")


# --- exception handlers ---

@bot.exception_handler(VKAPIError)
async def on_vk_error(error: VKAPIError, message: Message) -> None:
    await message.answer(f"VK API вернул ошибку: {error}")


@bot.exception_handler(RuntimeError)
async def on_runtime_error(error: RuntimeError, message: Message) -> None:
    await message.answer(f"RuntimeError: {error}")


# catch-all — сработает для всего, что не поймали выше
@bot.exception_handler()
async def on_any_error(error: Exception, message: Message) -> None:
    await message.answer(f"Неизвестная ошибка: {type(error).__name__}: {error}")


if __name__ == "__main__":
    bot.run_polling()
