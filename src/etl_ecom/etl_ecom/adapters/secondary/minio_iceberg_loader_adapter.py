from duckdb import DuckDBPyConnection

from etl_ecom.application.ports.secondary.iceberg_loader_port import IcebergLoaderPort
from etl_ecom.ingestion.loader_to_iceberg import load_all_tables_minio_to_iceberg


class MinioIcebergLoaderAdapter(IcebergLoaderPort):
    def __init__(self, conn: DuckDBPyConnection):
        self._conn = conn

    def load(self, run_id: str) -> int:
        return load_all_tables_minio_to_iceberg(run_id, self._conn)
