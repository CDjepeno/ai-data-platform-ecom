from datetime import datetime
import io

import pandas as pd

from etl_ecom.db.engine import get_minio_client, get_source_engine
from etl_ecom.ingestion.raw_query_builder import build_query
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)

TABLES = [
    "users",
    "customers",
    "products",
    "orders",
]

def run_raw():
    
    logger.info("🥉 Preparing bronze ingestion tasks")
    
    source_engine = get_source_engine()
    s3_client = get_minio_client()

    bucket = "ecom-etl"

    for table in TABLES:
        
        logger.info(f"📥 Extracting table: {table}")

        query = build_query(table)
        
        df = pd.read_sql(query, source_engine)

        logger.info(f"📊 Rows extracted: {len(df)}")

        # convert to parquet (in memory)
        file_key = f"bronze/{table}/{table}.parquet"
        
        df.to_parquet("/tmp/data.parquet", index=False)
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        key = f"raw/postgres/{table}/ingestion_date={today}/part-000.parquet"

        # upload to MinIO
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)

        s3_client.put_object(
            Bucket="ecom-etl",
            Key=key,
            Body=buffer.getvalue()
        )

        logger.info(f"✅ Uploaded to MinIO: {file_key}")

    logger.info("🚀 Bronze ingestion completed")