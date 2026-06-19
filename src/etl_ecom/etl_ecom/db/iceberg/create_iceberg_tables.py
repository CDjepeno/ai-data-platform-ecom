from etl_ecom.db.engine import get_duckdb_connection
from etl_ecom.scripts.iceberg.iceberg import get_iceberg_catalog
from etl_ecom.db.mapper.arrow_iceberg_mapper import arrow_to_iceberg_schema
from etl_ecom.ingestion.config.table_config import TABLE_CONFIG
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def create_iceberg_tables():
    catalog = get_iceberg_catalog()
    con = get_duckdb_connection()

    try:
        try:
            catalog.create_namespace("raw")
            logger.info("✅ Namespace raw created")
        except Exception:
            logger.info("ℹ️ Namespace raw already exists")

        for table_name in TABLE_CONFIG.keys():

            full_name = f"raw.{table_name}"

            try:

                catalog.load_table(full_name)
                logger.info(f"✅ {full_name} already exists")
                continue

            except Exception:
                pass

            logger.info(f"🆕 Creating Iceberg table: {full_name}")

            arrow_table = con.execute(f"""
                SELECT *,
                'init' AS run_id
                FROM postgres_db.public.{table_name}
                LIMIT 0
            """).fetch_arrow_table()

            schema = arrow_to_iceberg_schema(arrow_table.schema)

            catalog.create_table(
                identifier=full_name, schema=schema
            )

    finally:
        con.close()

        logger.info(f"✅ Table created: {full_name}")
