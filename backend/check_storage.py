import boto3
from botocore.config import Config

from app.core.config import settings

from app.core.config import settings
from app.core.storage import s3_client, ensure_bucket_exists


if __name__ == "__main__":
    ensure_bucket_exists()

    response = s3_client.head_bucket(Bucket=settings.s3_bucket)
    print(f"Bucket '{settings.s3_bucket}' доступен.")
    print(f"HTTP status: {response['ResponseMetadata']['HTTPStatusCode']}")

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.s3_access_key_id,
    aws_secret_access_key=settings.s3_secret_access_key,
    region_name=settings.s3_region,
    config=Config(
        signature_version="s3v4",
        connect_timeout=3,
        read_timeout=10,
        retries={"max_attempts": 2},
    ),
)


def ensure_bucket_exists() -> None:
    try:
        s3_client.head_bucket(Bucket=settings.s3_bucket)
    except Exception as exc:
        from botocore.exceptions import ClientError

        if not isinstance(exc, ClientError):
            raise

        error_code = exc.response.get("Error", {}).get("Code", "")
        status_code = exc.response.get("ResponseMetadata", {}).get(
            "HTTPStatusCode"
        )

        if error_code not in ("404", "NoSuchBucket", "NotFound") and status_code != 404:
            raise

        s3_client.create_bucket(Bucket=settings.s3_bucket)