from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


async def get_active_products(session: AsyncSession) -> list[Product]:
    statement = (
        select(Product)
        .where(Product.is_active.is_(True))
        .order_by(Product.created_at.desc(), Product.id)
    )

    result = await session.scalars(statement)
    return list(result.all())