-- watermark_upsert.sql
-- Met à jour ou insère le watermark pour une table donnée
-- Utilise UPSERT (INSERT OR REPLACE) pour gérer les mises à jour
-- sqlfluff: disable=PRS
INSERT OR REPLACE INTO metadata.etl_watermark
(table_name, high_watermark, watermark_id)
VALUES (?, ?, ?);
