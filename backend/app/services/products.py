from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.services.storage import upload_product_image


async def create_product(
    session: AsyncSession,
    *,
    title: str,
    description: str | None,
    image_data: bytes,
    content_type: str,
    price=None,
    currency: str | None = None,
) -> Product:
    image_key = upload_product_image(image_data, content_type)

    product = Product(
        title=title,
        description=description,
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