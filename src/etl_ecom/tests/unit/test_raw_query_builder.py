import duckdb
import pytest

from etl_ecom.application.raw_query_builder import build_query


class TestBuildQuery:
    """Unit tests for the incremental SQL query builder.

    build_query() produces a SELECT statement for a given table.
    - Non-incremental tables → simple SELECT with no filter.
    - Incremental tables with no existing watermark → full load (no WHERE).
    - Incremental tables with an existing watermark → filtered SELECT.

    We pass an in-memory DuckDB connection pre-seeded with the watermark table
    so no real database or Postgres connection is required.
    """

    # ── Non-incremental tables ──────────────────────────────────────────────

    def test_non_incremental_table_returns_simple_select(
        self, duckdb_with_metadata: duckdb.DuckDBPyConnection
    ):
        # "branches" has incremental: false in ingestion_config.yml
        query = build_query("branches", duckdb_with_metadata)
        assert "SELECT * FROM postgres_db.public.branches" in query
        assert "WHERE" not in query

    def test_non_incremental_table_categories_returns_simple_select(
        self, duckdb_with_metadata: duckdb.DuckDBPyConnection
    ):
        query = build_query("categories", duckdb_with_metadata)
        assert "SELECT * FROM postgres_db.public.categories" in query
        assert "WHERE" not in query

    # ── Incremental tables — initial load (no watermark row) ────────────────

    def test_incremental_table_with_no_watermark_returns_full_load(
        self, duckdb_with_metadata: duckdb.DuckDBPyConnection
    ):
        # "users" has incremental: true but the watermark table is empty
        query = build_query("users", duckdb_with_metadata)
        assert "SELECT * FROM postgres_db.public.users" in query
        assert "WHERE" not in query

    def test_incremental_table_orders_with_no_watermark_returns_full_load(
        self, duckdb_with_metadata: duckdb.DuckDBPyConnection
    ):
        query = build_query("orders", duckdb_with_metadata)
        assert "SELECT * FROM postgres_db.public.orders" in query
        assert "WHERE" not in query

    # ── Incremental tables — subsequent load (watermark exists) ─────────────

    def test_incremental_table_with_watermark_adds_where_clause(
        self, duckdb_with_metadata: duckdb.DuckDBPyConnection
    ):
        duckdb_with_metadata.execute("""
            INSERT INTO metadata.etl_watermark VALUES
            ('users', '2026-01-01 00:00:00', 100)
        """)
        query = build_query("users", duckdb_with_metadata)
        assert "WHERE" in query
        assert "updated_at" in query
        assert "2026-01-01 00:00:00" in query

    def test_incremental_query_filters_by_watermark_id(
        self, duckdb_with_metadata: duckdb.DuckDBPyConnection
    ):
        duckdb_with_metadata.execute("""
            INSERT INTO metadata.etl_watermark VALUES
            ('users', '2026-03-15 12:00:00', 500)
        """)
        query = build_query("users", duckdb_with_metadata)
        # The OR clause handles rows with the same timestamp but higher ID
        assert "OR" in query
        assert "user_id" in query
        assert "500" in query

    def test_incremental_query_includes_order_by(
        self, duckdb_with_metadata: duckdb.DuckDBPyConnection
    ):
        duckdb_with_metadata.execute("""
            INSERT INTO metadata.etl_watermark VALUES
            ('customers', '2026-02-01 00:00:00', 200)
        """)
        query = build_query("customers", duckdb_with_metadata)
        assert "ORDER BY" in query
        assert "updated_at" in query
        assert "customer_id" in query

    # ── Unknown / unconfigured table ─────────────────────────────────────────

    def test_table_not_in_config_falls_back_to_simple_select(
        self, duckdb_with_metadata: duckdb.DuckDBPyConnection
    ):
        # A table unknown to TABLE_CONFIG has no incremental config → simple SELECT
        query = build_query("campaigns", duckdb_with_metadata)
        assert "SELECT * FROM postgres_db.public.campaigns" in query
        assert "WHERE" not in query
