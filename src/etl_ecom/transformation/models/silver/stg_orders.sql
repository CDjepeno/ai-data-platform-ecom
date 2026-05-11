{{ config(
    materialized='table',
) }}

WITH source_data AS (
    SELECT  *
    FROM {{ source('raw', 'orders') }}
),

cleaned AS (
    SELECT  
    order_id,
    customer_id,
    branch_id,
    order_date,
    status,
    ingested_at,
    total_amount,
    created_at,
    updated_at,
    CURRENT_TIMESTAMP AS dbt_loaded_at,
    '{{ invocation_id }}' AS dbt_run_id,
    to_hex(
        md5(
            to_utf8(
                concat_ws(
                    '|',
                    CAST(customer_id AS VARCHAR),
                    CAST(branch_id AS VARCHAR),
                    coalesce(status, ''),
                    CAST(total_amount AS VARCHAR),
                    CAST(order_date AS VARCHAR)
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
            PARTITION BY order_id 
            ORDER BY updated_at DESC
        ) AS rn
    FROM cleaned
)


SELECT 
    order_id,
    customer_id,
    branch_id,
    order_date,
    status,
    ingested_at,
    total_amount,
    created_at,
    updated_at,
    dbt_loaded_at,
    row_hash,
    dbt_run_id
FROM deduplicated
WHERE rn = 1