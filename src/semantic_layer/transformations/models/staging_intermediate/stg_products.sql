{{ config(
    materialized='table',
) }}

WITH source_data AS (
    SELECT *
    FROM {{ source('raw', 'products') }}
),

cleaned AS (
    SELECT
        product_id,
        product_sku,
        COALESCE(TRIM(name), 'Unknown') AS name,
        TRIM(description)               AS description,
        price,
        created_at,
        updated_at,
        ingested_at,
        CURRENT_TIMESTAMP               AS dbt_loaded_at,
        '{{ invocation_id }}'           AS dbt_run_id,
        to_hex(
            md5(
                to_utf8(
                    concat_ws(
                        '|',
                        COALESCE(TRIM(name), ''),
                        CAST(price AS VARCHAR),
                        COALESCE(product_sku, '')
                    )
                )
            )
        ) AS row_hash
    FROM source_data
),

deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY updated_at DESC
        ) AS rn
    FROM cleaned
)

SELECT
    product_id,
    product_sku,
    name,
    description,
    price,
    created_at,
    updated_at,
    ingested_at,
    dbt_loaded_at,
    dbt_run_id,
    row_hash
FROM deduplicated
WHERE rn = 1
