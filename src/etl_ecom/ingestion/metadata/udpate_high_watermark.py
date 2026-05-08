from pathlib import Path
import traceback

from duckdb import DuckDBPyConnection

from etl_ecom.ingestion.config.table_config import TABLE_CONFIG
from etl_ecom.ingestion.raw_query_builder import build_query
from etl_ecom.utils.load_sql_files import load_sql_file
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def update_high_watermark(
    table: str,
    warehouse_engine: DuckDBPyConnection
) -> None:

    try:
        logger.info(f"🔥 update watermark appelé pour {table}")

        config = TABLE_CONFIG.get(table)

        if not config:
            logger.warning(f"⚠️ No config found for table {table}")
            return

        incremental_cfg = config.get("incremental", {})

        if not incremental_cfg.get("enabled", False):
            logger.info(f"ℹ️ Incremental disabled for {table}")
            return

        column = incremental_cfg.get("watermark_column")
        watermark_id_col = incremental_cfg.get("watermark_id", "id")

        if not column:
            logger.warning(f"⚠️ No watermark column configured for {table}")
            return

        # 🔨 rebuild source query
        query = build_query(table, warehouse_engine)

        # 📊 récupérer dernière watermark + id
        watermark_query = f"""
            SELECT
                {column} AS watermark_value,
                {watermark_id_col} AS watermark_id
            FROM (
                {query}
            )
            ORDER BY {column} DESC, {watermark_id_col} DESC
            LIMIT 1
        """

        result = warehouse_engine.execute(watermark_query).fetchone()

        if not result:
            logger.warning(f"⚠️ No rows found for watermark update on {table}")
            return

        new_watermark, last_id = result

        # 📄 SQL path
        BASE_DIR = Path(__file__).resolve().parents[2]
        sql_path = BASE_DIR / "sql/metadata/upsert_watermark.sql"

        sql_query = load_sql_file(sql_path)

        if not sql_query:
            raise ValueError(
                "❌ Impossible de charger upsert_watermark.sql"
            )

        # 🚀 upsert watermark
        warehouse_engine.execute(
            sql_query,
            [table, new_watermark, int(last_id)]
        )

        logger.info(
            f"✅ Watermark updated for {table}: "
            f"{new_watermark} (id={last_id})"
        )

    except Exception as e:
        logger.error(f"❌ Erreur update_high_watermark pour {table}")
        logger.error(f"👉 Message: {e}")
        logger.error(traceback.format_exc())
        raise