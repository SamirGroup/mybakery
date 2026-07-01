import asyncio

from aiogram import Bot

from bot.config import BOT_TOKEN, WEBHOOK_SECRET, WEBHOOK_URL


async def main() -> None:
    if not WEBHOOK_URL:
        raise SystemExit("WEBHOOK_URL .env faylida ko'rsatilmagan")

    bot = Bot(token=BOT_TOKEN)
    await bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET or None,
        drop_pending_updates=True,
    )
    info = await bot.get_webhook_info()
    print("Webhook o'rnatildi:", info.url)
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
