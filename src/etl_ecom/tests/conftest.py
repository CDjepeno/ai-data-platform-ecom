import duckdb
import pytest


@pytest.fixture
def duckdb_with_metadata() -> duckdb.DuckDBPyConnection:
    """In-memory DuckDB with the metadata schema pre-created.

    Shared by any test that needs to interact with the watermark table
    without hitting a real database.
    """
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE SCHEMA metadata")
    conn.execute("""
        CREATE TABLE metadata.etl_watermark (
            table_name   TEXT PRIMARY KEY,
            high_watermark TIMESTAMP,
            watermark_id INT
        )
    """)
    yield conn
    conn.close()
