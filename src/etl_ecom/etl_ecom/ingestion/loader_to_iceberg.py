
from pathlib import Path
import time

import pyarrow as pa
from duckdb import DuckDBPyConnection
from etl_ecom.db.engine import configure_duckdb_s3
from etl_ecom.scripts.iceberg.iceberg import get_iceberg_catalog
from etl_ecom.db.mapper.arrow_iceberg_mapper import arrow_to_iceberg_schema
from etl_ecom.ingestion.config.table_config import TABLE_CONFIG
from etl_ecom.utils.logger import get_logger

_AIRBYTE_COLUMNS = frozenset({
    "_airbyte_raw_id",
    "_airbyte_extracted_at",
    "_airbyte_meta",
    "_airbyte_generation_id",
})


def _drop_airbyte_columns(df: pa.Table) -> pa.Table:
    cols_to_drop = [name for name in df.schema.names if name in _AIRBYTE_COLUMNS]
    return df.drop(cols_to_drop) if cols_to_drop else df


def _normalize_timestamps(df: pa.Table) -> pa.Table:
    """Cast non-UTC timezone-aware timestamps to UTC.

    PyIceberg only supports UTC for timestamptz. Airbyte may write timestamps
    with local timezones (e.g. Europe/Paris) that must be converted before append.
    """
    new_columns = []
    new_fields = []
    changed = False
    for i, field in enumerate(df.schema):
        col = df.column(i)
        if pa.types.is_timestamp(field.type) and field.type.tz not in (None, "UTC"):
            utc_type = pa.timestamp(field.type.unit, tz="UTC")
            new_columns.append(col.cast(utc_type))
            new_fields.append(field.with_type(utc_type))
            changed = True
        else:
            new_columns.append(col)
            new_fields.append(field)
    if not changed:
        return df
    return pa.table(new_columns, schema=pa.schema(new_fields))


SQL_TEMPLATE_DIR = Path(__file__).parent.parent / "sql" / "bronze"
BUCKET = "ecom-etl"

logger = get_logger(__name__)


def load_single_table_to_iceberg(
    table_name: str, run_id: str, conn: DuckDBPyConnection
) -> int:
    start = time.time()
    logger.info(f"📤 Loading {table_name} to Iceberg...")

    configure_duckdb_s3(conn)

    try:

        # 1. Read from MinIO via DuckDB — Airbyte writes Parquet to the raw layer.
        parquet_glob = f"s3://{BUCKET}/raw/airbyte/public/{table_name}/**/*.parquet"
        try:
            df = conn.execute(f"""
                SELECT
                    *,
                    CAST(NOW() AS TIMESTAMP) AS ingested_at,
                    '{run_id}' AS run_id
                FROM read_parquet('{parquet_glob}', union_by_name=true)
            """).fetch_arrow_table()
        except Exception as e:
            if "No files found" in str(e):
                logger.warning(f"⚠️ No Parquet files for {table_name} — skipping")
                return 0
            raise

        df = _drop_airbyte_columns(df)
        df = _normalize_timestamps(df)
        row_count = len(df)
        if row_count == 0:
            logger.warning(f"⚠️ No data for {table_name}")
            return 0

        # 2. Load Iceberg catalog
        catalog = get_iceberg_catalog()
        full_table_name = f"raw.{table_name}"

        # 3. Drop if exists — always recreate for a full reload so that stale
        # snapshot metadata from a previous partial run never breaks the append.
        try:
            catalog.drop_table(full_table_name)
            logger.info(f"🗑️ Dropped existing table {full_table_name}")
        except Exception:
            pass

        schema = arrow_to_iceberg_schema(df.schema)
        
        table = catalog.create_table(
            identifier=full_table_name, 
            schema=schema,
            location=f"s3://{BUCKET}/warehouse/raw/{table_name}")

        logger.info(f"🧊 Appending {row_count} rows into {full_table_name}")

        # 4. Write to Iceberg
        table.append(df)

        logger.info(f"✅ {table_name}: appended {row_count} rows")

        duration = round(time.time() - start, 2)

        logger.info(f"⏱️ {table_name} loaded in {duration}s")

        return row_count

    except Exception as e:
        logger.error(f"❌ Failed to load {table_name}: {e}")
        raise


_CAMPAIGN_TABLES = ["meta_campaigns", "tiktok_campaigns", "google_campaigns"]


def load_campaign_table_to_iceberg(
    table_name: str, run_id: str, conn: DuckDBPyConnection
) -> int:
    start = time.time()
    logger.info(f"📤 Loading campaign table {table_name} to Iceberg...")

    configure_duckdb_s3(conn)

    parquet_glob = f"s3://{BUCKET}/raw/marketing/{table_name}/**/*.parquet"
    try:
        df = conn.execute(f"""
            SELECT
                *,
                CAST(NOW() AS TIMESTAMP) AS ingested_at,
                '{run_id}' AS run_id
            FROM read_parquet('{parquet_glob}', union_by_name=true)
        """).fetch_arrow_table()
    except Exception as e:
        if "No files found" in str(e):
            logger.warning(f"⚠️ No Parquet files for {table_name} — skipping")
            return 0
        raise

    row_count = len(df)
    if row_count == 0:
        logger.warning(f"⚠️ No data for {table_name}")
        return 0

    catalog = get_iceberg_catalog()
    full_table_name = f"raw.{table_name}"

    try:
        catalog.drop_table(full_table_name)
        logger.info(f"🗑️ Dropped existing table {full_table_name}")
    except Exception:
        pass

    schema = arrow_to_iceberg_schema(df.schema)
    table = catalog.create_table(
        identifier=full_table_name,
        schema=schema,
        location=f"s3://{BUCKET}/warehouse/raw/{table_name}",
    )
    table.append(df)

    duration = round(time.time() - start, 2)
    logger.info(f"✅ {table_name}: appended {row_count} rows in {duration}s")
    return row_count


def load_all_tables_minio_to_iceberg(run_id: str, conn: DuckDBPyConnection) -> int:
    """Load all ecom tables and marketing campaign tables into Iceberg."""
    total = 0
    for table_name in TABLE_CONFIG.keys():
        total += load_single_table_to_iceberg(table_name, run_id, conn)
    for table_name in _CAMPAIGN_TABLES:
        total += load_campaign_table_to_iceberg(table_name, run_id, conn)

    logger.info(f"📊 Total rows loaded to iceberg: {total}")
    return total


def ensure_table_exists(catalog, table_name: str, schema) -> bool:
    """Create the table if missing; return True if it was created."""
    namespace = table_name.split(".")[0] if "." in table_name else None

    # Create namespace if needed
    if namespace:
        try:
            catalog.create_namespace(namespace)
            logger.info(f"✅ Namespace '{namespace}' created")
        except Exception:
            pass  # Already exists

    # Create table if needed
    try:
        catalog.load_table(table_name)
        return False
    except Exception:
        catalog.create_table(
            identifier=table_name,
            schema=schema,
            location=f"s3://{BUCKET}/warehouse/raw/{table_name}",
        )
        logger.info(f"✅ Table '{table_name}' created")
        return True
