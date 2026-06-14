import os


from pyiceberg.catalog import load_catalog
import s3fs

from etl_ecom.db.db_config import settings
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


os.environ["AWS_ACCESS_KEY_ID"] = settings.aws_access_key_id      
os.environ["AWS_SECRET_ACCESS_KEY"] = settings.aws_secret_access_key  
os.environ["AWS_ENDPOINT_URL"] = settings.minio_endpoint           
os.environ["AWS_DEFAULT_REGION"] = settings.minio_region           


s3fs.S3FileSystem.clear_instance_cache()   # ← clear cache


def get_iceberg_catalog():

    try:
        catalog = load_catalog(
            "nessie",
            **{
                "type": "rest",
                "uri": settings.nessie_uri,
                "warehouse": settings.iceberg_warehouse,
                "s3.endpoint": settings.minio_endpoint,
                "s3.access-key-id": settings.aws_access_key_id,
                "s3.secret-access-key": settings.aws_secret_access_key,
                "s3.region": settings.minio_region,
                "s3.path-style-access": "true",
                "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
            },
        )

        logger.info("✅ Iceberg catalog loaded")

        return catalog

    except Exception as e:
        logger.error(f"❌ Error loading Iceberg catalog: {e}")
        raise