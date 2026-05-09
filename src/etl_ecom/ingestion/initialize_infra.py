
from etl_ecom.db.minio.create_bucket import create_bucket
from etl_ecom.db.iceberg.create_iceberg_tables import create_iceberg_tables
from etl_ecom.db.init_db import init_db
from etl_ecom.utils.logger import get_logger


logger = get_logger(__name__)


def initialize_infra():
    """
    Initializes the infrastructure for the e-commerce data platform.
    This includes creating necessary buckets, initializing the database, and creating Iceberg tables.
    """
    logger.info("🔧 Initializing infrastructure...")
    
    init_db()
    
    create_bucket()
    
    create_iceberg_tables()
    
    logger.info("✅ Infrastructure initialized successfully.")