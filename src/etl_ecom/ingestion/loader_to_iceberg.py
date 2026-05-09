# src/etl_ecom/ingestion/loader.py

from pathlib import Path
import time

from sqlalchemy.exc import NoSuchTableError
from etl_ecom.db.engine import get_duckdb_connection, configure_duckdb_s3
from scripts.iceberg.iceberg import get_iceberg_catalog
from etl_ecom.db.mapper.arrow_iceberg_mapper import arrow_to_iceberg_schema
from etl_ecom.ingestion.config.table_config import TABLE_CONFIG
from etl_ecom.utils.logger import get_logger


SQL_TEMPLATE_DIR = Path(__file__).parent.parent / "sql" / "bronze"
BUCKET = "ecom-etl"

logger = get_logger(__name__)


def load_single_table_to_iceberg(table_name: str, run_id: str) -> int:
    start = time.time()
    logger.info(f"📤 Loading {table_name} to Iceberg...")

    conn = get_duckdb_connection()
    configure_duckdb_s3(conn)

    try:
       
        # 1. Lecture depuis MinIO via DuckDB
        df = conn.execute(f"""
            SELECT
                *,
                CAST(NOW() AS TIMESTAMP) AS ingested_at,
                '{run_id}' AS run_id

            FROM read_parquet(
                's3://{BUCKET}/raw/postgres/{table_name}/*/*.parquet',
                union_by_name = true
            )
        """).fetch_arrow_table()

        row_count = len(df)
        if row_count == 0:
            logger.warning(f"⚠️ No data for {table_name}")
            return 0

        # 2. Chargement catalogue Iceberg
        catalog = get_iceberg_catalog()
        full_table_name = f"raw.{table_name}"

        # 3. Création de la table si elle n'existe pas
        try:
            table = catalog.load_table(full_table_name)
        except NoSuchTableError:
            logger.info(f"🆕 Creating table {full_table_name}")


            # Inférer le schéma depuis le DataFrame PyArrow
            schema = arrow_to_iceberg_schema(df.schema)

            table = catalog.create_table(
                identifier=full_table_name,
                schema=schema
            )

        logger.info(
            f"🧊 Appending {row_count} rows into {full_table_name}"
        )
        
        # 4. Écriture dans Iceberg
        table.append(df)

        # 5. Vérification
        latest = table.scan().to_arrow()
        total_rows = latest.num_rows
        logger.info(f"✅ {table_name} loaded: {row_count} rows (total: {len(latest)})")
        
        logger.info(
            f"✅ {table_name}: appended {row_count} rows "
            f"(total iceberg rows: {total_rows})"
        )
        
        duration = round(time.time() - start, 2)

        logger.info(
            f"⏱️ {table_name} loaded in {duration}s"
        )

        return row_count

    except Exception as e:
        logger.error(f"❌ Failed to load {table_name}: {e}")
        raise
    finally:
        conn.close()


def load_all_tables_minio_to_iceberg(run_id: str) -> int:
    """Charge toutes les tables configurées."""
    total = 0
    for table_name in TABLE_CONFIG.keys():
        total += load_single_table_to_iceberg(table_name, run_id)
    
    logger.info(f"📊 Total rows loaded to iceberg: {total}")
    return total


def ensure_table_exists(catalog, table_name: str, schema) -> bool:
    """Crée la table si elle n'existe pas, retourne True si création."""
    namespace = table_name.split('.')[0] if '.' in table_name else None

    # Crée le namespace si besoin
    if namespace:
        try:
            catalog.create_namespace(namespace)
            logger.info(f"✅ Namespace '{namespace}' créé")
        except Exception:
            pass  # Déjà existant

    # Crée la table si besoin
    try:
        catalog.load_table(table_name)
        return False
    except NoSuchTableError:
        catalog.create_table(
            identifier=table_name,
            schema=schema,
            location=f"s3://ecom-etl/warehouse/{table_name}"
        )
        logger.info(f"✅ Table '{table_name}' crée")
        return True





