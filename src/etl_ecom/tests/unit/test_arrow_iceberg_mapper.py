import pyarrow as pa
from pyiceberg.types import (
    BooleanType,
    DecimalType,
    DoubleType,
    IntegerType,
    LongType,
    StringType,
    TimestampType,
    TimestamptzType,
)

from etl_ecom.db.mapper.arrow_iceberg_mapper import arrow_to_iceberg_schema


def _single_field_schema(arrow_type: pa.DataType):
    """Helper: wrap one Arrow type in a schema and convert it to Iceberg."""
    return arrow_to_iceberg_schema(pa.schema([pa.field("col", arrow_type)]))


class TestArrowToIcebergSchema:
    """Unit tests for the Arrow → Iceberg schema mapper.

    arrow_to_iceberg_schema() converts a PyArrow schema to a PyIceberg schema.
    It is a pure function: given an Arrow schema, it always produces the same
    Iceberg schema with no side effects.
    """

    # ── Type conversions ────────────────────────────────────────────────────

    def test_int64_maps_to_long_type(self):
        schema = _single_field_schema(pa.int64())
        assert isinstance(schema.fields[0].field_type, LongType)

    def test_int32_maps_to_integer_type(self):
        schema = _single_field_schema(pa.int32())
        assert isinstance(schema.fields[0].field_type, IntegerType)

    def test_string_maps_to_string_type(self):
        schema = _single_field_schema(pa.string())
        assert isinstance(schema.fields[0].field_type, StringType)

    def test_timestamp_without_timezone_maps_to_timestamp_type(self):
        schema = _single_field_schema(pa.timestamp("us"))
        assert isinstance(schema.fields[0].field_type, TimestampType)

    def test_timestamp_with_utc_timezone_maps_to_timestamptz_type(self):
        # Airbyte writes timezone-aware timestamps with tz=UTC after normalization
        schema = _single_field_schema(pa.timestamp("us", tz="UTC"))
        assert isinstance(schema.fields[0].field_type, TimestamptzType)

    def test_timestamp_with_non_utc_timezone_maps_to_timestamptz_type(self):
        # Europe/Paris arrives from Airbyte raw Parquet; _normalize_timestamps()
        # casts it to UTC before the mapper runs, but the mapper itself also maps
        # any tz-aware timestamp to TimestamptzType regardless of the tz name.
        schema = _single_field_schema(pa.timestamp("us", tz="Europe/Paris"))
        assert isinstance(schema.fields[0].field_type, TimestamptzType)

    def test_boolean_maps_to_boolean_type(self):
        schema = _single_field_schema(pa.bool_())
        assert isinstance(schema.fields[0].field_type, BooleanType)

    def test_float64_maps_to_double_type(self):
        schema = _single_field_schema(pa.float64())
        assert isinstance(schema.fields[0].field_type, DoubleType)

    def test_float32_maps_to_double_type(self):
        schema = _single_field_schema(pa.float32())
        assert isinstance(schema.fields[0].field_type, DoubleType)

    def test_decimal128_maps_to_decimal_type_with_correct_precision_and_scale(self):
        schema = _single_field_schema(pa.decimal128(10, 2))
        field_type = schema.fields[0].field_type
        assert isinstance(field_type, DecimalType)
        assert field_type.precision == 10
        assert field_type.scale == 2

    def test_dictionary_type_maps_to_string_type(self):
        # PostgreSQL enums arrive as Arrow dictionary<int32, utf8>
        dict_type = pa.dictionary(pa.int32(), pa.string())
        schema = _single_field_schema(dict_type)
        assert isinstance(schema.fields[0].field_type, StringType)

    def test_unknown_arrow_type_falls_back_to_string_type(self):
        # binary has no explicit mapping → StringType fallback
        schema = _single_field_schema(pa.binary())
        assert isinstance(schema.fields[0].field_type, StringType)

    # ── Schema structure ────────────────────────────────────────────────────

    def test_field_ids_are_sequential_starting_at_one(self):
        arrow_schema = pa.schema([
            pa.field("id", pa.int64()),
            pa.field("name", pa.string()),
            pa.field("price", pa.float64()),
        ])
        iceberg_schema = arrow_to_iceberg_schema(arrow_schema)
        assert [f.field_id for f in iceberg_schema.fields] == [1, 2, 3]

    def test_all_fields_are_optional(self):
        # required=False means the column is nullable — always true in this mapper
        arrow_schema = pa.schema([pa.field("col", pa.int64())])
        iceberg_schema = arrow_to_iceberg_schema(arrow_schema)
        assert iceberg_schema.fields[0].required is False

    def test_field_names_are_preserved(self):
        arrow_schema = pa.schema([
            pa.field("customer_id", pa.int64()),
            pa.field("email", pa.string()),
        ])
        iceberg_schema = arrow_to_iceberg_schema(arrow_schema)
        names = [f.name for f in iceberg_schema.fields]
        assert names == ["customer_id", "email"]

    def test_empty_schema_returns_empty_iceberg_schema(self):
        iceberg_schema = arrow_to_iceberg_schema(pa.schema([]))
        assert len(iceberg_schema.fields) == 0

    def test_multi_column_schema_preserves_all_types(self):
        # Mirrors the real products table structure
        arrow_schema = pa.schema([
            pa.field("product_id", pa.int64()),
            pa.field("product_sku", pa.string()),
            pa.field("name", pa.string()),
            pa.field("price", pa.decimal128(10, 2)),
            pa.field("created_at", pa.timestamp("us")),
        ])
        iceberg_schema = arrow_to_iceberg_schema(arrow_schema)
        types = [type(f.field_type) for f in iceberg_schema.fields]
        assert types == [LongType, StringType, StringType, DecimalType, TimestampType]
