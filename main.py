import asyncio
import logging

from bot.core import create_bot, create_dispatcher
from bot.database.engine import init_db


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await init_db()

    bot = create_bot()
    dp = create_dispatcher()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
