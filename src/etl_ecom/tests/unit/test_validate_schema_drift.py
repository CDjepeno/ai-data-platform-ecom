import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from etl_ecom.application.schema_validation.validate_schema_drift import (
    get_iceberg_schema,
    main,
)


# ─── Test helpers ─────────────────────────────────────────────────────────────

def _field(name: str, type_str: str) -> MagicMock:
    f = MagicMock()
    f.name = name
    f.field_type = type_str
    return f


def _catalog(namespace_tables: dict) -> MagicMock:
    """Build a mock Iceberg catalog.

    namespace_tables: {('raw',): {'products': [field, ...], ...}, ...}
    """
    catalog = MagicMock()
    catalog.list_namespaces.return_value = list(namespace_tables.keys())

    def list_tables(ns):
        return [(ns[0], name) for name in namespace_tables.get(ns, {})]

    def load_table(identifier):
        ns = (identifier[0],)
        name = identifier[1]
        fields = namespace_tables[ns][name]
        table = MagicMock()
        table.schema.return_value.fields = fields
        return table

    catalog.list_tables.side_effect = list_tables
    catalog.load_table.side_effect = load_table
    return catalog


def _conn(pg_rows: list[dict]) -> MagicMock:
    """Build a mock DuckDB connection returning the given rows as a DataFrame.

    pg_rows: [{'table_name': ..., 'column_name': ..., 'data_type': ...}]
    """
    conn = MagicMock()
    conn.execute.return_value.fetchdf.return_value = pd.DataFrame(
        pg_rows or [],
        columns=["table_name", "column_name", "data_type"],
    )
    return conn


PATCH_CATALOG = "etl_ecom.application.schema_validation.validate_schema_drift.get_iceberg_catalog"
PATCH_SQL = "etl_ecom.application.schema_validation.validate_schema_drift.load_sql_file"


# ─── get_iceberg_schema ───────────────────────────────────────────────────────

class TestGetIcebergSchema:

    def test_returns_all_fields_for_raw_table(self):
        # Regression: the inner debug loop used to shadow the outer `field` variable,
        # causing only the last field (run_id) to be appended for every iteration.
        fields = [
            _field("product_id", "int"),
            _field("name", "string"),
            _field("price", "decimal(10, 2)"),
            _field("ingested_at", "timestamptz"),
        ]
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {'products': fields}})):
            result = get_iceberg_schema()

        assert len(result) == 4
        assert [r["column_name"] for r in result] == [
            "product_id", "name", "price", "ingested_at"
        ]

    def test_each_field_has_correct_type(self):
        fields = [_field("price", "decimal(10, 2)"), _field("id", "int")]
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {'orders': fields}})):
            result = get_iceberg_schema()

        assert result[0] == {"table_name": "orders", "column_name": "price", "data_type": "decimal(10, 2)"}
        assert result[1] == {"table_name": "orders", "column_name": "id", "data_type": "int"}

    def test_skips_non_raw_namespaces(self):
        with patch(PATCH_CATALOG, return_value=_catalog({
            ('raw',): {'orders': [_field("id", "long")]},
            ('silver',): {'orders_clean': [_field("id", "long")]},
        })):
            result = get_iceberg_schema()

        assert all(r["table_name"] == "orders" for r in result)
        assert len(result) == 1

    def test_multiple_raw_tables_all_returned(self):
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {
            'products': [_field("id", "int")],
            'orders': [_field("order_id", "long"), _field("total", "double")],
        }})):
            result = get_iceberg_schema()

        assert len(result) == 3
        table_names = [r["table_name"] for r in result]
        assert table_names.count("products") == 1
        assert table_names.count("orders") == 2

    def test_empty_catalog_returns_empty_list(self):
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {}})):
            assert get_iceberg_schema() == []


# ─── main — schema drift comparison ──────────────────────────────────────────

class TestSchemaDriftMain:

    def test_matching_schemas_pass(self):
        fields = [
            _field("product_id", "int"),
            _field("name", "string"),
            _field("ingested_at", "timestamptz"),   # excluded — should not cause drift
        ]
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {'products': fields}})):
            with patch(PATCH_SQL, return_value="SELECT 1"):
                main(_conn([
                    {"table_name": "products", "column_name": "product_id", "data_type": "integer"},
                    {"table_name": "products", "column_name": "name", "data_type": "character varying"},
                ]))

    def test_column_missing_from_iceberg_raises(self):
        # Iceberg has product_id but NOT product_sku → drift
        fields = [_field("product_id", "int")]
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {'products': fields}})):
            with patch(PATCH_SQL, return_value="SELECT 1"):
                with pytest.raises(Exception, match="Schema drift detected"):
                    main(_conn([
                        {"table_name": "products", "column_name": "product_id", "data_type": "integer"},
                        {"table_name": "products", "column_name": "product_sku", "data_type": "character varying"},
                    ]))

    def test_extra_column_in_iceberg_raises(self):
        # Iceberg has product_id + old_column that no longer exists in PG → drift
        fields = [_field("product_id", "int"), _field("old_column", "string")]
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {'products': fields}})):
            with patch(PATCH_SQL, return_value="SELECT 1"):
                with pytest.raises(Exception, match="Schema drift detected"):
                    main(_conn([
                        {"table_name": "products", "column_name": "product_id", "data_type": "integer"},
                    ]))

    def test_table_absent_from_iceberg_is_skipped(self):
        # products exists in PG but not yet in Iceberg (will be created by load_to_iceberg)
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {}})):
            with patch(PATCH_SQL, return_value="SELECT 1"):
                main(_conn([
                    {"table_name": "products", "column_name": "product_id", "data_type": "integer"},
                ]))

    def test_pipeline_columns_in_iceberg_do_not_cause_extra_drift(self):
        # ingested_at, ingestion_date, run_id are added by the ETL — Iceberg has them,
        # PG does not. They must be silently ignored on both sides.
        fields = [
            _field("product_id", "int"),
            _field("ingested_at", "timestamptz"),
            _field("ingestion_date", "date"),
            _field("run_id", "string"),
        ]
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {'products': fields}})):
            with patch(PATCH_SQL, return_value="SELECT 1"):
                main(_conn([
                    {"table_name": "products", "column_name": "product_id", "data_type": "integer"},
                ]))

    def test_airbyte_metadata_columns_in_iceberg_do_not_cause_extra_drift(self):
        fields = [
            _field("product_id", "int"),
            _field("_airbyte_raw_id", "string"),
            _field("_airbyte_extracted_at", "timestamptz"),
            _field("_airbyte_meta", "string"),
            _field("_airbyte_generation_id", "long"),
        ]
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {'products': fields}})):
            with patch(PATCH_SQL, return_value="SELECT 1"):
                main(_conn([
                    {"table_name": "products", "column_name": "product_id", "data_type": "integer"},
                ]))

    def test_csv_tables_in_iceberg_are_fully_ignored(self):
        # Campaign tables come from CSV files, not PostgreSQL — must never be compared.
        campaign_fields = [_field("spend", "double"), _field("impressions", "long")]
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {
            'meta_campaigns': campaign_fields,
            'tiktok_campaigns': campaign_fields,
            'google_campaigns': campaign_fields,
        }})):
            with patch(PATCH_SQL, return_value="SELECT 1"):
                main(_conn([]))  # PG has no campaign data

    def test_type_mismatch_raises(self):
        # Iceberg has product_id as "string" but PG says it's "integer" → drift
        fields = [_field("product_id", "string")]
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {'products': fields}})):
            with patch(PATCH_SQL, return_value="SELECT 1"):
                with pytest.raises(Exception, match="Schema drift detected"):
                    main(_conn([
                        {"table_name": "products", "column_name": "product_id", "data_type": "integer"},
                    ]))

    def test_multiple_tables_all_validated(self):
        # Both products and orders must match; if one fails the whole thing raises.
        with patch(PATCH_CATALOG, return_value=_catalog({('raw',): {
            'products': [_field("product_id", "int")],
            'orders': [_field("order_id", "long")],
        }})):
            with patch(PATCH_SQL, return_value="SELECT 1"):
                main(_conn([
                    {"table_name": "products", "column_name": "product_id", "data_type": "integer"},
                    {"table_name": "orders", "column_name": "order_id", "data_type": "bigint"},
                ]))
