import hmac
import json

from aiogram import Bot
from fastapi import APIRouter, Header, HTTPException, Request, status

from app.bot.handlers import dispatcher
from app.core.config import settings

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


def verify_webhook_secret(received: str | None) -> bool:
    expected = settings.telegram_webhook_secret
    return bool(expected and received and hmac.compare_digest(received, expected))


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if not verify_webhook_secret(x_telegram_bot_api_secret_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook secret",
        )

    bot: Bot | None = getattr(request.app.state, "telegram_bot", None)
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram bot is not configured",
        )

    try:
        update_data = await request.json()
        from aiogram.types import Update

        update = Update.model_validate(update_data, context={"bot": bot})
        await dispatcher.feed_update(bot, update)
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Telegram update",
        ) from None

    return {"ok": True}