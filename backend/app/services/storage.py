import uuid
from io import BytesIO

from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.core.storage import s3_client

from botocore.exceptions import ClientError


MAX_IMAGE_SIZE = 10 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def upload_product_image(
    image_data: bytes,
    content_type: str,
) -> str:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Unsupported image type")

    if not image_data:
        raise ValueError("Image is empty")

    if len(image_data) > MAX_IMAGE_SIZE:
        raise ValueError("Image exceeds 10 MB")

    try:
        with Image.open(BytesIO(image_data)) as image:
            image.verify()

            expected_formats = {
                "image/jpeg": "JPEG",
                "image/png": "PNG",
                "image/webp": "WEBP",
            }
            if image.format != expected_formats[content_type]:
                raise ValueError("Image content does not match content type")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Invalid image file") from exc

    extension = ALLOWED_CONTENT_TYPES[content_type]
    object_key = f"products/{uuid.uuid4().hex}{extension}"

    s3_client.put_object(
        Bucket=settings.s3_bucket,
        Key=object_key,
        Body=image_data,
        ContentType=content_type,
    )

    return object_key

def download_product_image(object_key: str):
    try:
        response = s3_client.get_object(
            Bucket=settings.s3_bucket,
            Key=object_key,
        )
        return response
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in ("NoSuchKey", "404", "NotFound"):
            return None
        raise