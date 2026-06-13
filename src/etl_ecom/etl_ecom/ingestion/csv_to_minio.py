from pathlib import Path

import duckdb

from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def write_csv_dir_to_parquet(
    conn: duckdb.DuckDBPyConnection,
    csv_dir: Path,
    destination: str,
) -> int:
    """Read all CSVs in csv_dir, union them, and write a single Parquet file.

    destination can be a local path (for tests) or an s3:// URI (for MinIO).
    Returns the number of rows written, or 0 if no CSV files were found.
    """
    csv_files = list(csv_dir.glob("*.csv"))
    if not csv_files:
        logger.info("No CSV files found in %s — skipping", csv_dir)
        return 0

    glob_pattern = str(csv_dir / "*.csv")
    result = conn.execute(
        f"SELECT COUNT(*) FROM read_csv_auto('{glob_pattern}', union_by_name=true)"
    ).fetchone()
    row_count: int = result[0] if result else 0

    conn.execute(
        f"COPY (SELECT * FROM read_csv_auto('{glob_pattern}', union_by_name=true))"
        f" TO '{destination}' (FORMAT PARQUET)"
    )

    logger.info("Wrote %d rows to %s", row_count, destination)
    return row_count


def ingest_campaigns_to_minio(
    conn: duckdb.DuckDBPyConnection,
    csv_dir: Path,
    run_id: str,
    bucket: str = "ecom-etl",
) -> int:
    """Ingest all campaign CSVs from csv_dir into MinIO as a partitioned Parquet file."""
    ingestion_date = run_id[:8]  # "20260101_120000" → "20260101"
    destination = (
        f"s3://{bucket}/raw/marketing/campaigns"
        f"/ingestion_date={ingestion_date}/part-000.parquet"
    )
    return write_csv_dir_to_parquet(conn, csv_dir, destination)
