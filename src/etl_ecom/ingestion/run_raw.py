from datetime import datetime

from etl_ecom.ingestion.config.table_config import TABLE_CONFIG
from etl_ecom.ingestion.run_raw_table import run_raw_table


def run_raw():
    run_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    for table in TABLE_CONFIG.keys():
        run_raw_table(table, run_id)