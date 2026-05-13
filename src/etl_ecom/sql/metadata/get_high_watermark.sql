-- watermark.sql
-- Fetches the latest watermark (value and ID) for a given table
-- Uses the dedicated metadata.etl_watermark table

WITH watermark_data AS (
    -- Select the most recent watermark for this table
    SELECT
        high_watermark,
        watermark_id,
        table_name
    FROM metadata.etl_watermark
    WHERE
        table_name = ?
)

-- Return watermark fields
SELECT
    high_watermark,
    COALESCE(watermark_id, 0) AS watermark_id
FROM watermark_data;
