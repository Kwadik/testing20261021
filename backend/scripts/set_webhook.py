import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aiogram import Bot

from app.bot.handlers import dispatcher
from app.core.config import settings


async def main() -> int:
    token = settings.telegram_bot_token
    base_url = settings.telegram_webapp_url.strip().rstrip("/")
    secret = settings.telegram_webhook_secret

    if not token:
        print("Ошибка: TELEGRAM_BOT_TOKEN не задан в .env.")
        return 1

    if not base_url.startswith("https://"):
        print("Ошибка: TELEGRAM_WEBAPP_URL должен начинаться с https://.")
        return 1

    if not secret:
        print("Ошибка: TELEGRAM_WEBHOOK_SECRET не задан в .env.")
        return 1

    webhook_url = f"{base_url}/api/v1/telegram/webhook"
    bot = Bot(token=token)

    try:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=secret,
            allowed_updates=dispatcher.resolve_used_update_types(),
        )

        info = await bot.get_webhook_info()

        if info.url != webhook_url:
            print("Ошибка: Telegram не подтвердил ожидаемый URL webhook.")
            return 1

        print("Webhook успешно установлен.")
        print(f"URL: {info.url}")
        print(f"Ожидающих обновлений: {info.pending_update_count}")
        print("Секрет и токен не выводятся.")
        return 0

    except Exception as exc:
        print(f"Ошибка установки webhook: {type(exc).__name__}")
        return 1

    finally:
        await bot.session.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
