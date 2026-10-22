from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionFactory
from app.repositories.product import get_active_products
from app.schemas.product import ProductRead

router = APIRouter(prefix="/api/v1/products", tags=["products"])


async def get_session():
    async with SessionFactory() as session:
        yield session


@router.get("", response_model=list[ProductRead])
async def list_products(
    session: AsyncSession = Depends(get_session),
) -> list[ProductRead]:
    products = await get_active_products(session)
    return [ProductRead.model_validate(product) for product in products]