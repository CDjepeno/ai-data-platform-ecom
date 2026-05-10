{{ config(materialized='table') }}

WITH source_data AS (
    SELECT  *
    FROM {{ source('raw', 'customers') }}

),

cleaned AS (
    SELECT  
    customer_id,
    user_id,
    TRIM(first_name) AS firstname,
    TRIM(last_name) AS lastname,
    phone,
    address,
    city,
    country,
    created_at,
    updated_at,
    ingested_at,
    CURRENT_TIMESTAMP AS dbt_loaded_at ,
    '{{ invocation_id }}' AS dbt_run_id,
    to_hex(
        md5(
            to_utf8(
                concat_ws(
                    '|',
                    CAST(customer_id AS VARCHAR)
                    coalesce(TRIM(first_name), ''),
                    coalesce(TRIM(last_name), '')
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
            PARTITION BY customer_id 
            ORDER BY updated_at DESC
        ) AS rn
    FROM cleaned
)


SELECT  
    customer_id,
    firstname,
    lastname,
    phone,
    address,
    city,
    country,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_run_id,
    row_hash
FROM deduplicated
WHERE rn = 1


