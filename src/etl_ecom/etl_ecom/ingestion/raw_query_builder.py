from duckdb import DuckDBPyConnection

from etl_ecom.ingestion.config.table_config import TABLE_CONFIG
from etl_ecom.ingestion.metadata.get_high_watermark import get_high_watermark_rows
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def build_query(table: str, warehouse_engine: DuckDBPyConnection) -> str:
    """
    Build the SQL query to extract data from a table.
    Supports incremental mode with a watermark.
    """
    table_config = TABLE_CONFIG.get(table, {})

    query = f"SELECT * FROM postgres_db.public.{table}"

    incremental_cfg = table_config.get("incremental", {})

    # Incremental mode: fetch only new rows
    if incremental_cfg.get("enabled"):
        watermark_column = incremental_cfg.get("watermark_column")
        watermark_id_column = incremental_cfg.get("watermark_id", "id")

        if not watermark_column:
            logger.warning(
                f"⚠️  Table {table}: incremental enabled but watermark_column is missing"
            )
            return query + ";"

        # Fetch the latest known watermark
        watermark_rows = get_high_watermark_rows(table, warehouse_engine)

        if watermark_rows:
            high_watermark = watermark_rows["high_watermark"]
            watermark_id = watermark_rows["watermark_id"]

            # Build the filter with the correct columns
            query += f"""
                WHERE
                    {watermark_column} > TIMESTAMP '{high_watermark}'
                    OR (
                        {watermark_column} = TIMESTAMP '{high_watermark}'
                        AND {watermark_id_column} > {watermark_id}
                    )
                ORDER BY {watermark_column}, {watermark_id_column}
                """
        else:
            logger.info(f"  📦 Initial load for {table} (no existing watermark)")

    return query
