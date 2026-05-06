from datetime import datetime
import io
from botocore.exceptions import ClientError

import pandas as pd

from etl_ecom.db.engine import (
    get_duckdb_connection,
    get_minio_client,
    get_source_engine
)
from etl_ecom.ingestion.metadata.log_row_metrics import log_row_metrics
from etl_ecom.ingestion.metadata.udpate_high_watermark import update_high_watermark
from etl_ecom.ingestion.raw_query_builder import build_query
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def run_raw_table(table: str, run_id: str | None = None):

    logger.info(f"🥉 Start ingestion for table: {table}")

    source_engine = get_source_engine()
    s3_client = get_minio_client()
    con = get_duckdb_connection()

    bucket = "ecom-etl"
    
    ensure_bucket_exists(s3_client, bucket)

    try:
        logger.info(f"📥 Extracting table: {table}")

        query = build_query(table, con)
        df = pd.read_sql(query, source_engine)

        logger.info(f"📊 {table} → {len(df)} rows")

        # 📦 upload parquet
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"raw/postgres/{table}/ingestion_date={today}/part-000.parquet"

        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)

        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=buffer.getvalue()
        )

        # 📊 metrics
        log_row_metrics(
            con=con,
            run_id=run_id,
            table_name=table,
            processed_at=datetime.now(),
            records_failed=0,
            rows_inserted=len(df),
            rows_updated=0,
            rows_deleted=0,
            rows_unchanged=0,
        )

        # 💧 watermark
        update_high_watermark(
            table=table,
            df=df,
            warehouse_engine=con
        )

        logger.info(f"✅ Table {table} done")

    except Exception as e:
        logger.error(f"❌ Error processing {table}: {e}")
        raise  # 🔥 important pour Airflow (fail task)

    finally:
        con.close()


def ensure_bucket_exists(s3_client, bucket: str):
    try:
        s3_client.head_bucket(Bucket=bucket)
        logger.info(f"🪣 Bucket already exists: {bucket}")

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code in ("404", "NoSuchBucket"):
            logger.info(f"🪣 Creating bucket: {bucket}")
            s3_client.create_bucket(Bucket=bucket)
        else:
            logger.error(f"❌ Unexpected error checking bucket: {e}")
            raise