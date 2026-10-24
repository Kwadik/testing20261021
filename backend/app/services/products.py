from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.services.storage import (
    download_product_image,
    upload_product_image,
)
from app.repositories.product import (
    get_active_product_by_id,
)
from app.repositories.category import (
    get_category_by_id,
    get_category_by_slug,
)


class ProductCategoryNotFoundError(Exception):
    pass

async def create_product(
    session: AsyncSession,
    *,
    category_id: UUID | None = None,
    title: str,
    description: str | None,
    image_data: bytes,
    content_type: str,
    price=None,
    currency: str | None = None,
) -> Product:
    if category_id is None:
        category = await get_category_by_slug(session, "uncategorized")
        if category is None:
            raise ProductCategoryNotFoundError(
                "Default category not found"
            )
        category_id = category.id
    else:
        category = await get_category_by_id(session, category_id)
        if category is None:
            raise ProductCategoryNotFoundError("Category not found")

    image_key = upload_product_image(image_data, content_type)

    product = Product(
        title=title,
        description=description,
        category_id=category_id,
        image_key=image_key,
        price=price,
        currency=currency,
    )

    try:
        session.add(product)
        await session.commit()
        await session.refresh(product)
    except Exception:
        await session.rollback()

        # Если запись в БД не сохранилась, удаляем загруженный объект.
        from app.core.config import settings
        from app.core.storage import s3_client

        s3_client.delete_object(
            Bucket=settings.s3_bucket,
            Key=image_key,
        )
        raise

    return product

async def get_product_image(
    session: AsyncSession,
    product_id: UUID,
) -> tuple[bytes, str] | None:
    product = await get_active_product_by_id(session, product_id)

    if product is None or not product.image_key:
        return None

    response = download_product_image(product.image_key)

    if response is None:
        return None

    body = response["Body"]

    try:
        content_type = response.get(
            "ContentType",
            "application/octet-stream",
        )
        image_data = body.read()
    finally:
        body.close()

    return image_data, content_type