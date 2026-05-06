

from datetime import datetime

from etl_ecom.db.intit_db import init_db
from etl_ecom.ingestion.metadata.step_runs import finish_step_run, start_step_run
from etl_ecom.ingestion.minio_to_duckdb import load_all_tables_to_duckdb
from etl_ecom.ingestion.run_raw import run_raw
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)

def main():

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    init_db()

    logger.info("🚀 Starting Pipeline")

    run_raw(run_id)
    

    try:
        rows_loaded = load_all_tables_to_duckdb(run_id)
    except Exception as e:
        raise

    logger.info(f"📊 Total rows loaded: {rows_loaded}")
    logger.info("🏁 Pipeline finished 🌞")
    
    
if __name__ == "__main__":
    main()
