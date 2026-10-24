from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.categories import (
    CategoryCycleError,
    CategoryNotFoundError,
    CategorySlugConflictError,
    create_category,
    list_categories,
    update_category,
)

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def get_categories_endpoint(
    session: AsyncSession = Depends(get_session),
) -> list[CategoryRead]:
    return await list_categories(session)


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category_endpoint(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_session),
) -> CategoryRead:
    try:
        return await create_category(session, data)
    except CategorySlugConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category slug already exists",
        ) from None
    except CategoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from None


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category_endpoint(
    category_id: UUID,
    data: CategoryUpdate,
    session: AsyncSession = Depends(get_session),
) -> CategoryRead:
    try:
        return await update_category(
            session,
            category_id,
            data.model_dump(exclude_unset=True),
        )
    except CategoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from None
    except CategorySlugConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category slug already exists",
        ) from None
    except CategoryCycleError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Category cannot be its own ancestor",
        ) from None
