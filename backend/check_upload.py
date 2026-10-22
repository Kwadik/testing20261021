from io import BytesIO

from PIL import Image

from app.core.config import settings
from app.core.storage import s3_client
from app.services.storage import upload_product_image


if __name__ == "__main__":
    buffer = BytesIO()

    # Создаём маленькое настоящее PNG-изображение без дополнительных файлов.
    Image.new("RGB", (32, 32), color="red").save(buffer, format="PNG")
    image_data = buffer.getvalue()

    object_key = upload_product_image(image_data, "image/png")

    # Проверяем, что объект действительно доступен в S3.
    response = s3_client.head_object(
        Bucket=settings.s3_bucket,
        Key=object_key,
    )

    print(f"Upload successful: {object_key}")
    print(f"Content-Type: {response['ContentType']}")
    print(f"Size: {response['ContentLength']} bytes")