from pathlib import Path

import duckdb

from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def write_single_csv_to_parquet(
    conn: duckdb.DuckDBPyConnection,
    csv_file: Path,
    destination: str,
) -> int:
    """Read one CSV file and write it as a Parquet file.

    destination can be a local path (for tests) or an s3:// URI (for MinIO).
    Returns the number of rows written, or 0 if the file is empty.
    """
    result = conn.execute(
        f"SELECT COUNT(*) FROM read_csv('{csv_file}', delim=',', header=true, strict_mode=false)"
    ).fetchone()
    row_count: int = result[0] if result else 0

    if row_count == 0:
        logger.warning("⚠️ No rows in %s — skipping", csv_file.name)
        return 0

    logger.info("📤 %s → MinIO (%d rows)", csv_file.stem, row_count)
    conn.execute(
        f"COPY (SELECT * FROM read_csv('{csv_file}', delim=',', header=true, strict_mode=false))"
        f" TO '{destination}' (FORMAT PARQUET)"
    )

    logger.info("✅ %s ingested", csv_file.stem)
    return row_count


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
        logger.warning("⚠️ No CSV files found in %s — skipping", csv_dir)
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

    logger.info("✅ Wrote %d rows to %s", row_count, destination)
    return row_count


def ingest_campaigns_to_minio(
    conn: duckdb.DuckDBPyConnection,
    csv_dir: Path,
    run_id: str,
    bucket: str = "ecom-etl",
) -> int:
    """Ingest each campaign CSV into MinIO as its own Parquet file.

    Each CSV (meta_campaigns.csv, tiktok_campaigns.csv, google_campaigns.csv)
    becomes a separate table in the raw layer: raw.meta_campaigns, etc.
    """
    ingestion_date = run_id[:8]
    logger.info("📂 Ingesting campaign CSVs (run=%s)...", run_id)
    total = 0
    for csv_file in sorted(csv_dir.glob("*.csv")):
        table_name = csv_file.stem
        destination = (
            f"s3://{bucket}/raw/marketing/{table_name}"
            f"/ingestion_date={ingestion_date}/part-000.parquet"
        )
        total += write_single_csv_to_parquet(conn, csv_file, destination)
    logger.info("📊 Campaign ingestion complete — %d rows", total)
    return total
