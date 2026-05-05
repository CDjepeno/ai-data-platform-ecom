CREATE TABLE IF NOT EXISTS metadata.etl_watermark (
    table_name TEXT PRIMARY KEY,
    high_watermark TIMESTAMP,
    watermark_id INT
);
