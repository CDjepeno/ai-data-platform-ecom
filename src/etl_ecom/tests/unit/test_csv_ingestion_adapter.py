from collections.abc import Iterator
from pathlib import Path

import duckdb
import pytest

from etl_ecom.ingestion.csv_to_minio import write_csv_dir_to_parquet


# ── Minimal CSV fixtures ────────────────────────────────────────────────────

META_CSV = """\
campaign_id,campaign_name,platform,owner,product_sku,start_date,end_date,budget_eur,impressions,clicks,conversions,spend_eur,revenue_eur,status
META-001,Laptop Launch,meta,Alice Martin,SKU-LAPTOP-PRO,2026-01-01,2026-02-01,1000.00,10000,200,10,900.00,12999.90,completed
META-002,Mouse Promo,meta,Lucas Dupont,SKU-MOUSE-GAMING,2026-02-01,2026-03-01,500.00,5000,100,5,450.00,299.95,active
"""

TIKTOK_CSV = """\
campaign_id,campaign_name,platform,owner,product_sku,start_date,end_date,budget_eur,impressions,clicks,conversions,spend_eur,revenue_eur,status
TK-001,Speaker Viral,tiktok,Thomas Girard,SKU-SPEAKER-BT,2026-01-10,2026-02-10,300.00,200000,2000,60,295.00,3599.40,completed
"""


@pytest.fixture
def conn() -> Iterator[duckdb.DuckDBPyConnection]:
    c = duckdb.connect(":memory:")
    yield c
    c.close()


class TestWriteCsvDirToParquet:
    """Unit tests for the CSV → Parquet core logic.

    write_csv_dir_to_parquet() accepts any destination path (local or S3),
    so tests use tmp_path to avoid any real MinIO dependency.
    """

    # ── Empty / missing data ────────────────────────────────────────────────

    def test_returns_zero_when_directory_is_empty(
        self, conn: duckdb.DuckDBPyConnection, tmp_path: Path
    ):
        output = str(tmp_path / "out.parquet")
        result = write_csv_dir_to_parquet(conn, tmp_path, output)
        assert result == 0

    def test_returns_zero_when_directory_has_no_csv_files(
        self, conn: duckdb.DuckDBPyConnection, tmp_path: Path
    ):
        (tmp_path / "readme.txt").write_text("not a csv")
        output = str(tmp_path / "out.parquet")
        result = write_csv_dir_to_parquet(conn, tmp_path, output)
        assert result == 0

    def test_does_not_create_parquet_file_when_no_csvs_found(
        self, conn: duckdb.DuckDBPyConnection, tmp_path: Path
    ):
        output_path = tmp_path / "out.parquet"
        write_csv_dir_to_parquet(conn, tmp_path, str(output_path))
        assert not output_path.exists()

    # ── Single file ─────────────────────────────────────────────────────────

    def test_returns_correct_row_count_for_single_csv(
        self, conn: duckdb.DuckDBPyConnection, tmp_path: Path
    ):
        (tmp_path / "meta.csv").write_text(META_CSV)
        output = str(tmp_path / "out.parquet")
        result = write_csv_dir_to_parquet(conn, tmp_path, output)
        assert result == 2

    def test_writes_readable_parquet_file(
        self, conn: duckdb.DuckDBPyConnection, tmp_path: Path
    ):
        (tmp_path / "meta.csv").write_text(META_CSV)
        output = str(tmp_path / "out.parquet")

        write_csv_dir_to_parquet(conn, tmp_path, output)

        df = conn.execute(f"SELECT * FROM read_parquet('{output}')").fetchdf()
        assert len(df) == 2

    def test_preserves_all_campaign_columns(
        self, conn: duckdb.DuckDBPyConnection, tmp_path: Path
    ):
        (tmp_path / "meta.csv").write_text(META_CSV)
        output = str(tmp_path / "out.parquet")

        write_csv_dir_to_parquet(conn, tmp_path, output)

        df = conn.execute(f"SELECT * FROM read_parquet('{output}')").fetchdf()
        expected = {
            "campaign_id", "campaign_name", "platform", "owner", "product_sku",
            "start_date", "end_date", "budget_eur", "impressions", "clicks",
            "conversions", "spend_eur", "revenue_eur", "status",
        }
        assert expected.issubset(set(df.columns))

    # ── Multiple files ──────────────────────────────────────────────────────

    def test_merges_multiple_csv_files_into_single_parquet(
        self, conn: duckdb.DuckDBPyConnection, tmp_path: Path
    ):
        (tmp_path / "meta.csv").write_text(META_CSV)
        (tmp_path / "tiktok.csv").write_text(TIKTOK_CSV)
        output = str(tmp_path / "out.parquet")

        result = write_csv_dir_to_parquet(conn, tmp_path, output)

        assert result == 3  # 2 meta + 1 tiktok

    def test_merged_parquet_contains_rows_from_all_platforms(
        self, conn: duckdb.DuckDBPyConnection, tmp_path: Path
    ):
        (tmp_path / "meta.csv").write_text(META_CSV)
        (tmp_path / "tiktok.csv").write_text(TIKTOK_CSV)
        output = str(tmp_path / "out.parquet")

        write_csv_dir_to_parquet(conn, tmp_path, output)

        platforms = conn.execute(
            f"SELECT DISTINCT platform FROM read_parquet('{output}') ORDER BY platform"
        ).fetchall()
        assert [p[0] for p in platforms] == ["meta", "tiktok"]
