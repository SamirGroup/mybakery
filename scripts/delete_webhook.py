import asyncio

from aiogram import Bot

from bot.config import BOT_TOKEN


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook o'chirildi. Endi 'python main.py' bilan polling rejimida ishlatishingiz mumkin.")
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
