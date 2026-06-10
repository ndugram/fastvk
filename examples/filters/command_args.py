"""
CommandArgs example — parse arguments from bot commands.

from fastvk.filters import CommandArgs

CommandArgs is injected automatically when Command filter matches.
Access args by index, use .get() with a default, or check len/bool.
"""
from fastvk import FastVK, Router
from fastvk.filters import Command, CommandArgs
from fastvk.types import Message

BOT_TOKEN = ""
GROUP_ID = 1234567

bot = FastVK(token=BOT_TOKEN, group_id=GROUP_ID)
router = Router()
bot.include_router(router)


@router.message(Command("ban"))
async def ban(message: Message, args: CommandArgs) -> None:
    if not args:
        await message.answer("Использование: /ban <user_id> [причина]")
        return
    user_id = args[0]
    reason = args.get(1, "без причины")
    await message.answer(f"Пользователь {user_id} заблокирован. Причина: {reason}")


@router.message(Command("say"))
async def say(message: Message, args: CommandArgs) -> None:
    if not args:
        await message.answer("Использование: /say <текст>")
        return
    await message.answer(args.text)


@router.message(Command("roll"))
async def roll(message: Message, args: CommandArgs) -> None:
    import random
    sides = int(args[0]) if args and args[0].isdigit() else 6
    await message.answer(f"🎲 {random.randint(1, sides)}")


if __name__ == "__main__":
    bot.run_polling()
