

from datetime import datetime

from etl_ecom.db.engine import get_duckdb_connection
from etl_ecom.ingestion.initialize_infra import initialize_infra
from etl_ecom.ingestion.loader_to_iceberg import load_all_tables_minio_to_iceberg
from etl_ecom.ingestion.run_raw import  ingest_raw_to_minio
from etl_ecom.ingestion.schema_validation.validate_schema_drift import main as validate_schema_drift
from etl_ecom.transformation.run_dbt_build import run_dbt_build
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def main():

    logger.info("🚀 Starting Pipeline")
    
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    conn = get_duckdb_connection()
    
    initialize_infra()
    
    validate_schema_drift(conn)
    
    ingest_raw_to_minio(run_id)
    
    load_all_tables_minio_to_iceberg(run_id , conn)
    
    run_dbt_build()

    
    logger.info("🏁 Pipeline finished 🌞")
    
    
if __name__ == "__main__":
    main()
