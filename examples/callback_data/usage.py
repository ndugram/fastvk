from typing import ClassVar

from fastvk import FastVK
from fastvk.callback_data import CallbackData
from fastvk.filters import Command
from fastvk.keyboard import Button, Keyboard
from fastvk.types import CallbackQuery, Message

bot = FastVK(token="vk1.a.YOUR_TOKEN")


class ProductCallback(CallbackData):
    prefix: ClassVar[str] = "product"
    product_id: int
    action: str = "view"


class ConfirmCallback(CallbackData):
    prefix: ClassVar[str] = "confirm"
    item_id: int
    user_id: int


@bot.message(Command("shop"))
async def shop(message: Message) -> None:
    kb = Keyboard(inline=True).row(
        Button.callback(
            "Товар 1",
            payload=ProductCallback(product_id=1).pack(),
        ),
        Button.callback(
            "Товар 2",
            payload=ProductCallback(product_id=2).pack(),
        ),
    )
    await message.answer("Выберите товар:", keyboard=kb)


@bot.message(Command("confirm"))
async def confirm(message: Message) -> None:
    cb = ConfirmCallback(item_id=42, user_id=message.from_id)
    await message.answer(
        "Подтвердите действие",
        keyboard=Keyboard(inline=True).row(
            Button.callback("Да", payload=cb.pack()),
            Button.callback(
                "Нет",
                payload=ConfirmCallback(
                    item_id=42, user_id=message.from_id, action="cancel"
                ).pack(),
            ),
        ),
    )


@bot.callback()
async def on_product(callback: CallbackQuery) -> None:
    cb = ProductCallback.unpack(callback.payload)
    await callback.answer(f"Товар #{cb.product_id}: {cb.action}")


@bot.callback()
async def on_confirm(callback: CallbackQuery) -> None:
    cb = ConfirmCallback.unpack(callback.payload)
    if cb.action == "cancel":
        await callback.answer("Отменено")
    else:
        await callback.answer(f"Подтверждено (item={cb.item_id})")


if __name__ == "__main__":
    bot.run_polling()
