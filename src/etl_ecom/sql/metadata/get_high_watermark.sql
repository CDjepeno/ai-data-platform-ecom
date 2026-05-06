-- watermark.sql
-- Récupère le dernier watermark (valeur et ID) pour une table donnée
-- Utilise la table metadata.etl_watermark dédiée

WITH watermark_data AS (
    -- Sélectionne le watermark le plus récent pour cette table
    SELECT
        high_watermark,
        watermark_id,
        table_name
    FROM metadata.etl_watermark
    WHERE
        table_name = ?
)

-- Retourne les informations du watermark
SELECT
    high_watermark,
    COALESCE(watermark_id, 0) AS watermark_id
FROM watermark_data;
