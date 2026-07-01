from aiogram.types import Update
from fastapi import FastAPI, Request, Response

from bot.config import WEBHOOK_PATH, WEBHOOK_SECRET
from bot.core import create_bot, create_dispatcher
from bot.database.engine import init_db

app = FastAPI()
bot = create_bot()
dp = create_dispatcher()

_db_ready = False


async def _ensure_db() -> None:
    global _db_ready
    if not _db_ready:
        await init_db()
        _db_ready = True


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request) -> Response:
    if WEBHOOK_SECRET:
        header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header != WEBHOOK_SECRET:
            return Response(status_code=401)

    await _ensure_db()
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return Response(status_code=200)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
