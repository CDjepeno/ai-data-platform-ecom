from etl_ecom.db.db_config import settings
from etl_ecom.db.engine import get_minio_client
from etl_ecom.utils.logger import get_logger
from botocore.exceptions import ClientError

logger = get_logger(__name__)


def create_bucket():
    s3_client = get_minio_client()
    bucket = settings.minio_bucket
    try:
        s3_client.head_bucket(Bucket=bucket)
        logger.info(f"🪣 Bucket already exists: {bucket}")

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code in ("404", "NoSuchBucket"):
            logger.info(f"🪣 Creating bucket: {bucket}")
            s3_client.create_bucket(Bucket=bucket)
        else:
            logger.error(f"❌ Unexpected error checking bucket: {e}")
            raise
