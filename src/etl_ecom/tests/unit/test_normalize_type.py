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
            # Airbyte promotes all integer types to int64 (long) when writing Parquet.
            # normalize_type must treat int and long as the same so drift checks pass.
            ("integer", "long"),
            ("smallint", "long"),
            ("bigint", "long"),
            # Iceberg serializes IntegerType as "int" — must also normalize to "long"
            ("int", "long"),
            ("text", "string"),
            ("character varying", "string"),
            # Airbyte converts all timestamps to UTC, so both tz-naive and tz-aware
            # PostgreSQL columns become timestamptz on the Iceberg side.
            ("timestamp without time zone", "timestamptz"),
            ("timestamp with time zone", "timestamptz"),
            # Iceberg type strings that come back from PyIceberg str(field.field_type)
            ("timestamp", "timestamptz"),
            ("timestamptz", "timestamptz"),
            # Airbyte converts all numeric types to float64, so the Iceberg side
            # always gets "double". Normalize source types to the same canonical value.
            ("numeric", "double"),
            ("double precision", "double"),
            ("real", "double"),
            # Iceberg type strings from PyIceberg str(field.field_type)
            ("decimal", "double"),
            ("float", "double"),
            ("boolean", "boolean"),
            ("user-defined", "string"),  # PostgreSQL enums become strings
        ],
    )
    def test_known_types_are_mapped_correctly(self, pg_type: str, expected: str):
        assert normalize_type(pg_type) == expected

    # ── Decimal prefix handling ─────────────────────────────────────────────

    def test_decimal_with_precision_and_scale_normalizes_to_double(self):
        # "decimal(10,2)" starts with "decimal" → prefix match → "decimal" → alias → "double"
        assert normalize_type("decimal(10,2)") == "double"

    def test_decimal_with_large_precision_normalizes_to_double(self):
        assert normalize_type("decimal(38,10)") == "double"

    # ── Case insensitivity ──────────────────────────────────────────────────

    def test_normalizes_input_to_lowercase_before_lookup(self):
        assert normalize_type("INTEGER") == "long"
        assert normalize_type("TEXT") == "string"
        assert normalize_type("BIGINT") == "long"

    # ── Unknown types ───────────────────────────────────────────────────────

    def test_unknown_type_is_returned_unchanged(self):
        # If a Postgres type has no mapping, the function returns it as-is.
        # This is intentional: the schema drift checker will flag it.
        assert normalize_type("uuid") == "uuid"
        assert normalize_type("jsonb") == "jsonb"
        assert normalize_type("xml") == "xml"
