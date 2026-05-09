from pyiceberg.io.pyarrow import pyarrow_to_schema
from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.transforms import IdentityTransform

from etl_ecom.db.engine import get_duckdb_connection
from scripts.iceberg.iceberg import get_iceberg_catalog
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
            catalog.create_namespace("silver")
            catalog.create_namespace("mart")
            logger.info("✅ Namespace raw créé")
        except Exception:
            logger.info("ℹ️ Namespace raw existe déjà")

        for table_name in TABLE_CONFIG.keys():

            full_name = f"raw.{table_name}"

            try:
                
                catalog.load_table(full_name)
                logger.info(f"✅ {full_name} existe déjà")
                continue

            except Exception:
                pass
            
            
            logger.info(f"🆕 Création Iceberg table: {full_name}")

            arrow_table = con.execute(f"""
                SELECT *,
                CURRENT_TIMESTAMP AS ingested_at,
                CURRENT_DATE AS ingestion_date,
                'init' AS run_id  
                FROM postgres_db.public.{table_name}
                LIMIT 0
            """).fetch_arrow_table()

            schema = arrow_to_iceberg_schema(arrow_table.schema)

            ingestion_field = next(
                field for field in schema.fields
                if field.name == "ingestion_date"
            )

            partition_spec = PartitionSpec(
                PartitionField(
                    source_id=ingestion_field.field_id,
                    field_id=1000,
                    transform=IdentityTransform(),
                    name="ingestion_date"
                )
            )
            
            catalog.create_table(
                identifier=full_name,
                schema=schema,
                partition_spec=partition_spec
            )
        
    finally:
        con.close()

        logger.info(f"✅ Table créée: {full_name}")