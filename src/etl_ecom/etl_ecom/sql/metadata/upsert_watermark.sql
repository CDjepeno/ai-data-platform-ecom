-- watermark_upsert.sql
-- Updates or inserts the watermark for a given table
-- Uses UPSERT (INSERT OR REPLACE) to apply updates
-- sqlfluff:disable:PRS
INSERT OR REPLACE INTO metadata.etl_watermark
(table_name, high_watermark, watermark_id)
VALUES (?, ?, ?);
