import pytest

from etl_ecom.application.schema_validation.validate_schema_drift import normalize_type


class TestNormalizeType:
    """Unit tests for the PostgreSQL → Iceberg type normalizer.

    normalize_type() is a pure function: it takes a raw Postgres data_type
    string and returns its canonical Iceberg equivalent. No I/O, no state.
    """

    # ── Known mappings ──────────────────────────────────────────────────────

    @pytest.mark.parametrize(
        "pg_type, expected",
        [
            ("integer", "int"),
            ("smallint", "int"),
            ("bigint", "long"),
            ("text", "string"),
            ("character varying", "string"),
            ("timestamp without time zone", "timestamp"),
            ("timestamp with time zone", "timestamptz"),
            ("numeric", "decimal"),
            ("double precision", "double"),
            ("real", "float"),
            ("boolean", "boolean"),
            ("user-defined", "string"),  # PostgreSQL enums become strings
        ],
    )
    def test_known_types_are_mapped_correctly(self, pg_type: str, expected: str):
        assert normalize_type(pg_type) == expected

    # ── Decimal prefix handling ─────────────────────────────────────────────

    def test_decimal_with_precision_and_scale_normalizes_to_decimal(self):
        # "decimal(10,2)" starts with "decimal" → mapped to "decimal"
        assert normalize_type("decimal(10,2)") == "decimal"

    def test_decimal_with_large_precision_normalizes_to_decimal(self):
        assert normalize_type("decimal(38,10)") == "decimal"

    # ── Case insensitivity ──────────────────────────────────────────────────

    def test_normalizes_input_to_lowercase_before_lookup(self):
        assert normalize_type("INTEGER") == "int"
        assert normalize_type("TEXT") == "string"
        assert normalize_type("BIGINT") == "long"

    # ── Unknown types ───────────────────────────────────────────────────────

    def test_unknown_type_is_returned_unchanged(self):
        # If a Postgres type has no mapping, the function returns it as-is.
        # This is intentional: the schema drift checker will flag it.
        assert normalize_type("uuid") == "uuid"
        assert normalize_type("jsonb") == "jsonb"
        assert normalize_type("xml") == "xml"
