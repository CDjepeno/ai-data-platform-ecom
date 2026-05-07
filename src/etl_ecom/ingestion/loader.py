# src/etl_ecom/ingestion/loader.py

from pathlib import Path
from jinja2 import Template
from etl_ecom.db.engine import get_duckdb_connection, configure_duckdb_s3
from etl_ecom.ingestion.config.table_config import TABLE_CONFIG

SQL_TEMPLATE_DIR = Path(__file__).parent.parent / "sql" / "bronze"
BUCKET = "ecom-etl"

def load_single_table(table_name: str, run_id: str) -> int:
    """Charge UNE seule table depuis MinIO vers DuckDB via Jinja."""
    conn = get_duckdb_connection()
    configure_duckdb_s3(conn)

    # Rend le template SQL
    with open(SQL_TEMPLATE_DIR / "create_raw_table.sql") as f:
        sql = Template(f.read()).render(
            table_name=table_name,
            run_id=run_id,
            bucket=BUCKET
        )

    conn.execute(sql)

    result = conn.execute(
        f"SELECT COUNT(*) FROM bronze.raw_{table_name}"
    ).fetchone()

    count = result[0] if result else 0

    conn.close()
    return count


def load_all_tables(run_id: str) -> int:
    """Charge toutes les tables configurées."""
    total = 0
    for table_name in TABLE_CONFIG.keys():
        total += load_single_table(table_name, run_id)
    return total









