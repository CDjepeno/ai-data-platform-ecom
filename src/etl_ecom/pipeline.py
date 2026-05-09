

from datetime import datetime

from etl_ecom.ingestion.initialize_infra import initialize_infra
from etl_ecom.ingestion.loader_to_iceberg import load_all_tables_minio_to_iceberg
from etl_ecom.ingestion.run_raw import  ingest_raw_to_minio
from etl_ecom.ingestion.schema_validation.validate_schema_drift import main as validate_schema_drift
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)

def main():

    logger.info("🚀 Starting Pipeline")
    
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    initialize_infra()
    
    validate_schema_drift()
    
    ingest_raw_to_minio(run_id)
    
    load_all_tables_minio_to_iceberg(run_id)

    
    logger.info("🏁 Pipeline finished 🌞")
    
    
if __name__ == "__main__":
    main()
