from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN, REDIS_URL
from bot.handlers import admin, user


def create_bot() -> Bot:
    return Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def create_dispatcher() -> Dispatcher:
    if REDIS_URL:
        from aiogram.fsm.storage.redis import RedisStorage

        storage = RedisStorage.from_url(REDIS_URL)
    else:
        storage = MemoryStorage()

    dp = Dispatcher(storage=storage)
    dp.include_router(admin.router)
    dp.include_router(user.router)
    return dp
