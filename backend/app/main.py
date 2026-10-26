from contextlib import asynccontextmanager

from aiogram import Bot
from fastapi import FastAPI, HTTPException, status

from app.api.categories import router as categories_router
from app.api.products import router as products_router
from app.bot.webhook import router as telegram_router
from app.core.config import settings
from app.core.database import check_database, close_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    bot = None

    if settings.telegram_bot_token:
        bot = Bot(token=settings.telegram_bot_token)

    app.state.telegram_bot = bot

    try:
        yield
    finally:
        if bot is not None:
            await bot.session.close()
        await close_database()


app = FastAPI(
    title="Shop API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(products_router)
app.include_router(categories_router)
app.include_router(telegram_router)


@app.get("/health/live", tags=["Health"])
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def readiness():
    try:
        await check_database()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from None

    return {"status": "ready"}
