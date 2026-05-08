from datetime import datetime
from botocore.exceptions import ClientError


from etl_ecom.db.engine import (
    get_duckdb_connection,
    get_minio_client,
)
from etl_ecom.ingestion.metadata.log_row_metrics import log_row_metrics
from etl_ecom.ingestion.metadata.udpate_high_watermark import update_high_watermark
from etl_ecom.ingestion.raw_query_builder import build_query
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def run_raw_table(table: str, run_id: str | None = None):

    logger.info(f"🥉 Start ingestion for table: {table}")

    s3_client = get_minio_client()
    con = get_duckdb_connection()

    bucket = "ecom-etl"
    
    ensure_bucket_exists(s3_client, bucket)

    try:
        logger.info(f"📥 Extracting table: {table}")

        query = build_query(table, con)

        today = datetime.now().strftime("%Y-%m-%d")

        parquet_path = (
            f"s3://{bucket}/raw/postgres/{table}/"
            f"ingestion_date={today}/part-000.parquet"
        )
        
        logger.info(f"📦 Writing parquet to: {parquet_path}")


        con.execute(f"""
            COPY (
                {query}
            )
            TO '{parquet_path}'
            (
                FORMAT PARQUET,
                COMPRESSION ZSTD
            );
        """)
        
        result = con.execute(f"""
            SELECT COUNT(*)
            FROM ({query})
        """).fetchone()

        row_count = result[0] if result else 0

        logger.info(f"📊 {table} → {row_count} rows")
        

        # 📊 metrics
        log_row_metrics(
            con=con,
            run_id=run_id,
            table_name=table,
            processed_at=datetime.now(),
            records_failed=0,
            rows_inserted=row_count,
            rows_updated=0,
            rows_deleted=0,
            rows_unchanged=0,
        )

        # 💧 watermark
        update_high_watermark(
            table=table,
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