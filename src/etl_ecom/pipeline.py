

from datetime import datetime

from etl_ecom.db.create_bucket import create_bucket
from etl_ecom.db.init_db import init_db
from etl_ecom.db.create_iceberg_tables import create_iceberg_tables
from etl_ecom.ingestion.loader_to_iceberg import load_all_tables_to_iceberg
from etl_ecom.ingestion.run_raw import run_raw
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)

def main():

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    init_db()
    create_bucket()
    create_iceberg_tables() 
    

    logger.info("🚀 Starting Pipeline")

    run_raw(run_id)
    

    rows_loaded = load_all_tables_to_iceberg(run_id)

    logger.info(f"📊 Total rows loaded: {rows_loaded}")
    logger.info("🏁 Pipeline finished 🌞")
    
    
if __name__ == "__main__":
    main()
