from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


async def get_categories(session: AsyncSession) -> list[Category]:
    result = await session.scalars(
        select(Category).order_by(Category.name, Category.id)
    )
    return list(result.all())


async def get_category_by_id(
    session: AsyncSession,
    category_id: UUID,
) -> Category | None:
    return await session.get(Category, category_id)


async def get_category_by_slug(
    session: AsyncSession,
    slug: str,
) -> Category | None:
    result = await session.scalars(
        select(Category).where(Category.slug == slug)
    )
    return result.first()


async def create_category(
    session: AsyncSession,
    *,
    name: str,
    slug: str,
    parent_id: UUID | None,
) -> Category:
    category = Category(
        name=name,
        slug=slug,
        parent_id=parent_id,
    )
    session.add(category)
    await session.flush()
    return category
