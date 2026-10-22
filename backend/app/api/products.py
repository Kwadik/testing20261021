from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionFactory
from app.repositories.product import get_active_products
from app.schemas.product import ProductRead
from app.services.products import create_product

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

@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
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
        product = await create_product(
            session,
            title=title,
            description=description,
            image_data=image_data,
            content_type=image.content_type,
            price=price,
            currency=currency,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ProductRead.model_validate(product)