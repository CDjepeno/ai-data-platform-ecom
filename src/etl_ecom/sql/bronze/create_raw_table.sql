-- sql/bronze/create_raw_table.sql
CREATE OR REPLACE TABLE bronze.raw_{{ table_name }} AS
SELECT
    *,
    CURRENT_TIMESTAMP AS ingestion_time,
    '{{ run_id }}' AS run_id,
    'postgresql' AS data_source
FROM READ_PARQUET(
    's3://{{ bucket }}/raw/postgres/{{ table_name }}/*/*.parquet',
    hive_partitioning = true
)
