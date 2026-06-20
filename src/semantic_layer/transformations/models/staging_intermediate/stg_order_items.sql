{{ config(materialized='table') }}

WITH source_data AS (
    SELECT *
    FROM {{ source('raw', 'order_items') }}
),

cleaned AS (
    SELECT
        order_item_id,
        order_id,
        product_id,
        CAST(quantity AS BIGINT) AS quantity,
        CAST(price AS DOUBLE) AS price,
        quantity * price AS line_total,
        created_at,
        updated_at,
        CURRENT_TIMESTAMP AS dbt_loaded_at,
        '{{ invocation_id }}' AS dbt_run_id,
        TO_HEX(MD5(TO_UTF8(CONCAT_WS(
            '|',
            CAST(order_item_id AS VARCHAR),
            CAST(order_id AS VARCHAR),
            CAST(product_id AS VARCHAR),
            CAST(quantity AS VARCHAR),
            CAST(price AS VARCHAR)
        )))) AS row_hash
    FROM source_data
),

deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY order_item_id
            ORDER BY updated_at DESC
        ) AS rn
    FROM cleaned
)

SELECT
    order_item_id,
    order_id,
    product_id,
    quantity,
    price,
    line_total,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_run_id,
    row_hash
FROM deduplicated
WHERE rn = 1
