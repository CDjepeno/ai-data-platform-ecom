from pathlib import Path

import duckdb

from etl_ecom.application.ports.secondary.csv_ingestion_port import CsvIngestionPort
from etl_ecom.ingestion.csv_to_minio import ingest_campaigns_to_minio


class DuckdbCsvIngestionAdapter(CsvIngestionPort):
    def __init__(
        self,
        conn: duckdb.DuckDBPyConnection,
        csv_dir: Path,
        bucket: str = "ecom-etl",
    ):
        self._conn = conn
        self._csv_dir = csv_dir
        self._bucket = bucket

    def ingest(self, run_id: str) -> int:
        return ingest_campaigns_to_minio(self._conn, self._csv_dir, run_id, self._bucket)
