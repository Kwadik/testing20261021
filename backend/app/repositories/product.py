from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.category import Category



async def get_active_products(
    session: AsyncSession,
    category_id: UUID | None = None,
) -> list[Product]:
    statement = select(Product).where(Product.is_active.is_(True))

    if category_id is not None:
        descendants = (
            select(Category.id)
            .where(Category.id == category_id)
            .cte("category_tree", recursive=True)
        )

        descendants = descendants.union_all(
            select(Category.id).join(
                descendants,
                Category.parent_id == descendants.c.id,
            )
        )

        statement = statement.where(
            Product.category_id.in_(select(descendants.c.id))
        )

    statement = statement.order_by(Product.created_at.desc(), Product.id)

    result = await session.scalars(statement)
    return list(result.all())


async def get_active_product_by_id(
    session: AsyncSession,
    product_id: UUID,
) -> Product | None:
    statement = select(Product).where(
        Product.id == product_id,
        Product.is_active.is_(True),
    )
    return await session.scalar(statement)