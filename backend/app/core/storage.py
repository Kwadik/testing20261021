import boto3
from botocore.config import Config

from app.core.config import settings


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