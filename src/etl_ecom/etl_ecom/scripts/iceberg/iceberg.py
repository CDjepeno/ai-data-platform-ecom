import s3fs as _s3fs

from pyiceberg.catalog import load_catalog

from etl_ecom.db.db_config import settings
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)

# s3fs caches directory listings by default. pyiceberg writes a file then
# immediately checks its size via s3fs — the stale cache causes FileNotFoundError.
# Patching here disables the cache for all s3fs instances used by pyiceberg.
_s3fs.S3FileSystem.clear_instance_cache()
_orig_s3fs_init = _s3fs.S3FileSystem.__init__


def _no_cache_s3fs_init(self, *args, **kwargs):
    kwargs.setdefault("use_listings_cache", False)
    _orig_s3fs_init(self, *args, **kwargs)


_s3fs.S3FileSystem.__init__ = _no_cache_s3fs_init


def get_iceberg_catalog():

    try:
        catalog = load_catalog(
            "nessie",
            **{
                "type": "rest",
                "uri": "http://nessie:19120/iceberg",
                "warehouse": "s3://ecom-etl/warehouse",
                "s3.endpoint": "http://minio:9000",
                "s3.access-key-id": settings.aws_access_key_id,
                "s3.secret-access-key": settings.aws_secret_access_key,
                "s3.region": "us-east-1",
                "s3.path-style-access": "true",
                "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
            },
        )

        logger.info("✅ Iceberg catalog loaded")

        return catalog

    except Exception as e:
        logger.error(f"❌ Error loading Iceberg catalog: {e}")
        raise
