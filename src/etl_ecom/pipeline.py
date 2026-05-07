

from datetime import datetime

from etl_ecom.db.intit_db import init_db
from etl_ecom.ingestion.loader import load_all_tables
from etl_ecom.ingestion.run_raw import run_raw
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)

def main():

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    init_db()

    logger.info("🚀 Starting Pipeline")

    run_raw(run_id)
    

    rows_loaded = load_all_tables(run_id)

    logger.info(f"📊 Total rows loaded: {rows_loaded}")
    logger.info("🏁 Pipeline finished 🌞")
    
    
if __name__ == "__main__":
    main()
