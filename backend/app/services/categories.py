from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category import (
    create_category as create_category_record,
    get_categories,
    get_category_by_id,
    get_category_by_slug,
)
from app.schemas.category import CategoryCreate


class CategoryNotFoundError(Exception):
    pass


class CategorySlugConflictError(Exception):
    pass


class CategoryCycleError(Exception):
    pass


async def list_categories(session: AsyncSession) -> list[Category]:
    return await get_categories(session)


async def create_category(
    session: AsyncSession,
    data: CategoryCreate,
) -> Category:
    if await get_category_by_slug(session, data.slug):
        raise CategorySlugConflictError

    if data.parent_id is not None:
        parent = await get_category_by_id(session, data.parent_id)
        if parent is None:
            raise CategoryNotFoundError("Parent category not found")

    try:
        category = await create_category_record(
            session,
            name=data.name,
            slug=data.slug,
            parent_id=data.parent_id,
        )
        await session.commit()
        await session.refresh(category)
        return category
    except IntegrityError as exc:
        await session.rollback()
        # Уникальность slug также должна обеспечиваться базой:
        # предварительная проверка сама по себе не защищает от гонки запросов.
        raise CategorySlugConflictError from exc
    except Exception:
        await session.rollback()
        raise


async def update_category(
    session: AsyncSession,
    category_id: UUID,
    changes: dict,
) -> Category:
    category = await get_category_by_id(session, category_id)
    if category is None:
        raise CategoryNotFoundError("Category not found")

    new_slug = changes.get("slug")
    if new_slug is not None and new_slug != category.slug:
        existing = await get_category_by_slug(session, new_slug)
        if existing is not None and existing.id != category.id:
            raise CategorySlugConflictError

    if "parent_id" in changes:
        new_parent_id = changes["parent_id"]

        if new_parent_id is not None:
            if new_parent_id == category.id:
                raise CategoryCycleError

            parent = await get_category_by_id(session, new_parent_id)
            if parent is None:
                raise CategoryNotFoundError("Parent category not found")

            # Поднимаемся по цепочке предков нового родителя.
            # Если встретим текущую категорию, возникнет цикл.
            visited: set[UUID] = set()
            current = parent

            while current is not None:
                if current.id == category.id:
                    raise CategoryCycleError

                if current.id in visited:
                    raise CategoryCycleError

                visited.add(current.id)

                if current.parent_id is None:
                    break

                current = await get_category_by_id(
                    session,
                    current.parent_id,
                )

        category.parent_id = new_parent_id

    if "name" in changes and changes["name"] is not None:
        category.name = changes["name"]

    if new_slug is not None:
        category.slug = new_slug

    try:
        await session.commit()
        await session.refresh(category)
        return category
    except IntegrityError as exc:
        await session.rollback()
        raise CategorySlugConflictError from exc
    except Exception:
        await session.rollback()
        raise
