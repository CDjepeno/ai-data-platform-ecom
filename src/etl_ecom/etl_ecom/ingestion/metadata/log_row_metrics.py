from datetime import datetime
from pathlib import Path
from duckdb import DuckDBPyConnection

from etl_ecom.utils.load_sql_files import load_sql_file


def log_row_metrics(
    con: DuckDBPyConnection,
    run_id: str | None,
    table_name: str,
    processed_at: datetime,
    records_failed: int,
    rows_inserted: int = 0,
    rows_updated: int = 0,
    rows_deleted: int = 0,
    rows_unchanged: int = 0,
) -> None:

    # 📄 load SQL
    BASE_DIR = Path(__file__).resolve().parents[2]
    sql_path = BASE_DIR / "sql/metadata/insert_row_metrics.sql"

    query = load_sql_file(sql_path)

    if not query:
        raise ValueError("❌ insert_row_metrics.sql not found")

    # 🚀 run in DuckDB
    con.execute(
        query,
        [
            run_id,
            table_name,
            rows_inserted,
            rows_updated,
            rows_deleted,
            rows_unchanged,
            records_failed,
            processed_at,
        ],
    )
