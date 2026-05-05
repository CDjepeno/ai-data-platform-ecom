

from etl_ecom.db.intit_db import init_db
from etl_ecom.ingestion.run_raw import run_raw
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    
    init_db()

    logger.info("🚀 Starting Pipeline")

    run_raw()

    logger.info("🏁 Pipeline finished 🌞")
    
    
    
if __name__ == "__main__":
    main()
