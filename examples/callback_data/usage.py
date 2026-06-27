from typing import ClassVar

from fastvk import FastVK, CallbackData
from fastvk.filters import CallbackDataFilter, Command
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
        Button.callback("Товар 1", payload=ProductCallback(product_id=1).pack()),
        Button.callback("Товар 2", payload=ProductCallback(product_id=2).pack()),
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



@bot.callback(CallbackDataFilter(ProductCallback))
async def on_product(callback: CallbackQuery, callback_data: ProductCallback) -> None:
    await callback.answer(f"Товар #{callback_data.product_id}: {callback_data.action}")


@bot.callback(CallbackDataFilter(ConfirmCallback))
async def on_confirm(callback: CallbackQuery, callback_data: ConfirmCallback) -> None:
    if callback_data.action == "cancel":
        await callback.answer("Отменено")
    else:
        await callback.answer(f"Подтверждено (item={callback_data.item_id})")


if __name__ == "__main__":
    bot.run_polling()
