from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from app.core.database import (
    check_database,
    close_database,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_database()


app = FastAPI(
    title="Shop API",
    version="0.1.0",
    lifespan=lifespan,
)


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