from datetime import datetime
import io
import logging
from typing import List, Optional
from pathlib import Path
import pandas as pd
from botocore.exceptions import ClientError

from etl_ecom.db.engine import get_duckdb_connection, get_minio_client
from etl_ecom.ingestion.config.table_config import TABLE_CONFIG


logger = logging.getLogger(__name__)

BUCKET = "ecom-etl"


def load_single_table_to_duckdb(s3_client, conn, table: str, run_id: str | None) -> int:
    logger.info(f"Loading table: {table} from Minio to DuckDB")

    prefix = f"raw/postgres/{table}/"

    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET, Prefix=prefix)

        if 'Contents' not in response:
            logger.warning(f"No files found for table {table} in Minio")
            return 0

        dfs = []
        for obj in response['Contents']:
            if obj['Key'].endswith('.parquet'):
                obj_response = s3_client.get_object(Bucket=BUCKET, Key=obj['Key'])
                buffer = io.BytesIO(obj_response['Body'].read())
                df = pd.read_parquet(buffer)
                dfs.append(df)

        if not dfs:
            logger.warning(f"No parquet files found for table {table}")
            return 0

        final_df = pd.concat(dfs, ignore_index=True)

        # Étape 1 : Créer une table temporaire DuckDB à partir du DataFrame
        conn.execute("CREATE OR REPLACE TEMP TABLE temp_final AS SELECT * FROM final_df")

        # Étape 2 : Lire le fichier SQL template et substituer les variables
        BASE_DIR = Path(__file__).resolve().parents[1]
        sql_path = BASE_DIR / "sql/bronze/create_raw_table.sql"
        
        
        with open(sql_path, 'r') as f:
            sql_template = f.read()

        # Substitution avec Template
        from string import Template
        sql = Template(sql_template).substitute(
            table_name=table,
            run_id=run_id
        )

        # Étape 3 : Exécuter le SQL (il référence temp_final)
        conn.execute(sql)

        # Étape 4 : Nettoyer la table temporaire
        conn.execute("DROP TABLE IF EXISTS temp_final")

        logger.info(f"{table}: {len(final_df)} rows loaded into bronze.raw_{table}")
        return len(final_df)

    except ClientError as e:
        logger.error(f"Minio error for {table}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error for {table}: {e}")
        raise


def load_all_tables_to_duckdb(run_id: str | None = None, tables: Optional[List[str]] = None) -> int:
    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    if tables is None:
        try:
            tables = list(TABLE_CONFIG.keys())
        except (ImportError, AttributeError):
            # Fallback sur les tables découvertes dans Minio
            tables = get_tables_in_minio()

    logger.info(f"Starting Minio to DuckDB loading for {len(tables)} tables")

    s3_client = get_minio_client()
    conn = get_duckdb_connection()

    total_rows = 0
    try:
        for table in tables:
            rows = load_single_table_to_duckdb(s3_client, conn, table, run_id)
            total_rows += rows

        logger.info(f"Loading completed: {total_rows} total rows loaded")

    except Exception as e:
        logger.error(f"Loading failed: {e}")
        raise
    finally:
        conn.close()

    return total_rows


def load_specific_table(table: str, run_id: str | None = None) -> int:
    s3_client = get_minio_client()
    conn = get_duckdb_connection()

    try:
        rows = load_single_table_to_duckdb(s3_client, conn, table, run_id)
        logger.info(f"{table}: {rows} rows loaded")
        return rows
    finally:
        conn.close()


def get_tables_in_minio() -> List[str]:
    s3_client = get_minio_client()
    tables = []
    response = s3_client.list_objects_v2(Bucket=BUCKET, Prefix="raw/postgres/", Delimiter='/')

    for prefix in response.get('CommonPrefixes', []):
        table_name = prefix['Prefix'].split('/')[-2]
        tables.append(table_name)

    return tables


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    

    if len(sys.argv) > 1:
        table = sys.argv[1]
        load_specific_table(table)
    else:
        load_all_tables_to_duckdb()