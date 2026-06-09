"""
Lifespan example — startup/shutdown hooks (FastAPI-style).

The @asynccontextmanager function runs code before `yield` on startup
and after `yield` on shutdown.
"""
from contextlib import asynccontextmanager

from fastvk import FastVK, Router
from fastvk.types import Message

TOKEN = "vk1.a.YOUR_TOKEN"
GROUP_ID = 123456789

router = Router()

# Fake "database" to show lifespan wiring
db: dict = {}


@asynccontextmanager
async def lifespan(bot: FastVK):
    # --- startup ---
    print("Bot starting, connecting to DB...")
    db["conn"] = "fake-connection"
    print(f"DB connected: {db['conn']}")

    yield  # bot is running here

    # --- shutdown ---
    print("Bot stopping, closing DB...")
    db.clear()
    print("DB closed.")


bot = FastVK(token=TOKEN, group_id=GROUP_ID, lifespan=lifespan)
bot.include_router(router)


@router.message()
async def echo(message: Message) -> None:
    conn = db.get("conn", "no connection")
    await message.answer(f"DB status: {conn}\nYou said: {message.text}")


if __name__ == "__main__":
    bot.run_polling()
