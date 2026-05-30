import asyncio
from datetime import datetime

from etl_ecom.db.engine import get_duckdb_connection
from etl_ecom.warehouse.warehouse_initialized import warehouse_initialized
from etl_ecom.ingestion.initialize_infra import initialize_infra
from etl_ecom.ingestion.loader_to_iceberg import load_all_tables_minio_to_iceberg
from etl_ecom.ingestion.run_raw import ingest_raw_to_minio
from etl_ecom.ingestion.schema_validation.validate_schema_drift import (
    main as validate_schema_drift,
)
from etl_ecom.utils.logger import get_logger
import httpx

logger = get_logger(__name__)


async def main():
    
    conn = get_duckdb_connection()
    
    if not warehouse_initialized(conn):

        logger.info("🚀 Starting Pipeline")

        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        conn = get_duckdb_connection()

        initialize_infra()

        validate_schema_drift(conn)

        ingest_raw_to_minio(run_id)

        load_all_tables_minio_to_iceberg(run_id, conn)

        async with httpx.AsyncClient(timeout=300) as client:

            logger.info("🔨 Building dbt...")
            response = await client.post(
                "http://semantic-layer:8001/build-dbt"
            )
            response.raise_for_status()

            logger.info("📦 Indexing semantic models...")
            response = await client.post(
                "http://semantic-layer:8001/index"
            )
            response.raise_for_status()


        logger.info("🏁 Pipeline finished 🌞")
    else:
        logger.info("✅ Warehouse already initialized")


if __name__ == "__main__":
    asyncio.run(main())
