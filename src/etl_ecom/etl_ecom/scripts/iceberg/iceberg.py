from pyiceberg.catalog import load_catalog

from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def get_iceberg_catalog():

    try:
        catalog = load_catalog(
            "nessie",
            **{
                "type": "rest",
                "uri": "http://nessie:19120/iceberg",
                "warehouse": "s3://ecom-etl/warehouse",
                "s3.endpoint": "http://minio:9000",
                "s3.endpoint-override": "http://minio:9000",
                "s3.access-key-id": "minioadmin",
                "s3.secret-access-key": "minioadmin",
                "s3.region": "us-east-1",
                "client.region": "us-east-1",
                # BOOLS
                "s3.path-style-access": True,
                "s3.resolve-region": False,
                "s3.force-virtual-addressing": False,
                "py-io-impl": "pyiceberg.io.fsspec.FsspecFileIO",
            },
        )

        logger.info("✅ Iceberg catalog loaded")

        return catalog

    except Exception as e:
        logger.error(f"❌ Error loading Iceberg catalog: {e}")
        raise
