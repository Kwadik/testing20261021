from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.api.dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product import (
    ProductRead,
    ProductCreate,
)
from app.repositories.product import (
    get_active_products,
    get_active_product_by_id,
)
from app.repositories.category import get_category_by_id

from app.services.storage import (
    download_product_image,
)
from app.services.products import (
    ProductCategoryNotFoundError,
    create_product,
    get_product_image as get_product_image_service,
)


router = APIRouter(prefix="/api/v1/products", tags=["products"])


def serialize_product(product) -> ProductRead:
    return ProductRead.model_validate(
        {
            "id": product.id,
            "category_id": product.category_id,
            "title": product.title,
            "description": product.description,
            "image_key": product.image_key,
            "image_url": (
                f"/api/v1/products/{product.id}/image"
                if product.image_key
                else "/images/product-placeholder.png"
            ),
            "price": product.price,
            "currency": product.currency,
            "created_at": product.created_at,
        }
    )


@router.get("", response_model=list[ProductRead])
async def list_products(
    category_id: UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[ProductRead]:
    if category_id is not None:
        category = await get_category_by_id(session, category_id)
        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

    products = await get_active_products(
        session,
        category_id=category_id,
    )
    return [serialize_product(product) for product in products]

@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
    category_id: UUID | None = Form(default=None),
    title: str = Form(min_length=1, max_length=255),
    description: str | None = Form(default=None),
    price: float | None = Form(default=None, ge=0),
    currency: str | None = Form(default=None, min_length=3, max_length=3),
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> ProductRead:
    if image.content_type not in {
        "image/jpeg",
        "image/png",
        "image/webp",
    }:
        raise HTTPException(status_code=415, detail="Unsupported image type")

    image_data = await image.read(10 * 1024 * 1024 + 1)
    if len(image_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image exceeds 10 MB")

    try:
        # Валидируем пользовательские параметры по правилам schema
        data = ProductCreate(
            title=title,
            category_id=category_id,
            description=description,
            price=Decimal(str(price)) if price is not None else None,
            currency=currency,
        )

        product = await create_product(
            session,
            title=data.title,
            category_id=data.category_id,
            description=data.description,
            image_data=image_data,
            content_type=image.content_type,
            price=data.price,
            currency=data.currency,
        )

    except ProductCategoryNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return serialize_product(product)

@router.get("/{product_id}/image", response_class=Response)
async def get_product_image_endpoint(
    product_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Response:
    result = await get_product_image_service(session, product_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Product or image not found",
        )

    image_data, content_type = result

    return Response(
        content=image_data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )