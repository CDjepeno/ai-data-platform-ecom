import pyarrow as pa

from etl_ecom.ingestion.loader_to_iceberg import _normalize_timestamps, _drop_airbyte_columns


class TestNormalizeTimestamps:
    """Unit tests for _normalize_timestamps().

    PyIceberg only accepts UTC for timezone-aware timestamps (TimestamptzType).
    Airbyte may write Parquet files with local timezones (e.g. Europe/Paris).
    _normalize_timestamps() casts those to UTC so PyIceberg can append them.
    It is a pure function: Arrow Table in, Arrow Table out, no I/O.
    """

    def test_utc_timestamp_column_is_returned_unchanged(self):
        schema = pa.schema([pa.field("ts", pa.timestamp("us", tz="UTC"))])
        table = pa.table({"ts": pa.array([1_000_000], type=pa.timestamp("us", tz="UTC"))})
        result = _normalize_timestamps(table)
        assert result.schema.field("ts").type == pa.timestamp("us", tz="UTC")

    def test_non_utc_timestamp_is_cast_to_utc(self):
        # Europe/Paris is the timezone Airbyte uses when writing French-locale data
        paris_type = pa.timestamp("us", tz="Europe/Paris")
        table = pa.table({"ts": pa.array([1_000_000], type=paris_type)})
        result = _normalize_timestamps(table)
        assert result.schema.field("ts").type == pa.timestamp("us", tz="UTC")

    def test_timezone_naive_timestamp_is_returned_unchanged(self):
        naive_type = pa.timestamp("us")
        table = pa.table({"ts": pa.array([1_000_000], type=naive_type)})
        result = _normalize_timestamps(table)
        assert result.schema.field("ts").type == naive_type

    def test_non_timestamp_columns_are_unchanged(self):
        schema = pa.schema([
            pa.field("id", pa.int64()),
            pa.field("name", pa.string()),
        ])
        table = pa.table({"id": pa.array([1]), "name": pa.array(["alice"])})
        result = _normalize_timestamps(table)
        assert result.schema == table.schema

    def test_only_non_utc_columns_are_modified_in_mixed_schema(self):
        paris_type = pa.timestamp("us", tz="Europe/Paris")
        utc_type = pa.timestamp("us", tz="UTC")
        naive_type = pa.timestamp("us")

        table = pa.table({
            "a": pa.array([1_000_000], type=paris_type),
            "b": pa.array([2_000_000], type=utc_type),
            "c": pa.array([3_000_000], type=naive_type),
            "d": pa.array([42], type=pa.int64()),
        })
        result = _normalize_timestamps(table)

        assert result.schema.field("a").type == pa.timestamp("us", tz="UTC")
        assert result.schema.field("b").type == utc_type
        assert result.schema.field("c").type == naive_type
        assert result.schema.field("d").type == pa.int64()

class TestDropAirbyteColumns:
    """Unit tests for _drop_airbyte_columns().

    Airbyte writes _airbyte_* metadata columns to every Parquet file.
    _airbyte_meta is a nested struct — PyIceberg cannot append it against a
    STRING schema. We drop all four metadata columns before creating the table.
    """

    def test_all_airbyte_columns_are_removed(self):
        table = pa.table({
            "user_id": pa.array([1]),
            "_airbyte_raw_id": pa.array(["abc"]),
            "_airbyte_extracted_at": pa.array([1_000_000], type=pa.timestamp("us", tz="UTC")),
            "_airbyte_generation_id": pa.array([0], type=pa.int64()),
            "_airbyte_meta": pa.array([{"sync_id": 1, "changes": []}], type=pa.struct([
                pa.field("sync_id", pa.int64()),
                pa.field("changes", pa.list_(pa.string())),
            ])),
        })
        result = _drop_airbyte_columns(table)
        assert result.column_names == ["user_id"]

    def test_table_without_airbyte_columns_is_returned_unchanged(self):
        table = pa.table({"id": pa.array([1]), "name": pa.array(["alice"])})
        result = _drop_airbyte_columns(table)
        assert result.schema == table.schema
        assert result.num_rows == 1

    def test_non_airbyte_columns_are_preserved(self):
        table = pa.table({
            "order_id": pa.array([42]),
            "amount": pa.array([9.99]),
            "_airbyte_raw_id": pa.array(["xyz"]),
        })
        result = _drop_airbyte_columns(table)
        assert set(result.column_names) == {"order_id", "amount"}


class TestDropThenNormalize:
    """Integration: _drop_airbyte_columns runs before _normalize_timestamps."""

    def test_airbyte_extracted_at_removed_before_timestamp_normalization(self):
        # _airbyte_extracted_at has tz=UTC — it must not reach _normalize_timestamps
        paris_type = pa.timestamp("us", tz="Europe/Paris")
        table = pa.table({
            "created_at": pa.array([1_000_000], type=paris_type),
            "_airbyte_extracted_at": pa.array([2_000_000], type=pa.timestamp("us", tz="UTC")),
        })
        result = _normalize_timestamps(_drop_airbyte_columns(table))
        assert result.column_names == ["created_at"]
        assert result.schema.field("created_at").type == pa.timestamp("us", tz="UTC")


class TestNormalizeTimestamps:
        paris_type = pa.timestamp("us", tz="Europe/Paris")
        utc_type = pa.timestamp("us", tz="UTC")
        # 2024-01-01 00:00:00 UTC = 1704067200000000 microseconds since epoch
        epoch_us = 1_704_067_200_000_000
        table = pa.table({"ts": pa.array([epoch_us], type=paris_type)})
        result = _normalize_timestamps(table)
        result_values = result.column("ts").cast(pa.int64())
        original_in_utc = pa.array([epoch_us], type=paris_type).cast(utc_type).cast(pa.int64())
        assert result_values[0].as_py() == original_in_utc[0].as_py()
